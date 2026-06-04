"""Main CLI entry point using Typer"""

from datetime import datetime
from pathlib import Path
from typing import Optional, List
import typer
from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from rich.text import Text

from cloudsoc.config.settings import get_settings
from cloudsoc.terraform.runner import TerraformRunner, TerraformStateError
from cloudsoc.aws.ec2 import EC2Service
from cloudsoc.aws.ssm import SSMService
from cloudsoc.orchestrator import (
    TerraformOrchestrator,
    DeploymentOrchestrator,
    DashboardOrchestrator,
    OrchestrationError,
)
from cloudsoc.utils.logger import logger, setup_logger

app = typer.Typer(help="Cloud SOC Infrastructure Orchestration Platform")
dashboard_app = typer.Typer(invoke_without_command=True)
deployment_app = typer.Typer()
ssm_app = typer.Typer()
console = Console()


def _render_error_panel(message: str) -> Panel:
    return Panel(Text(message, style="bold red"), expand=False)


@app.callback()
def setup(ctx: typer.Context) -> None:
    """Initialize settings and logging"""
    settings = get_settings()

    # Configure logging
    setup_logger(
        name="cloud-soc",
        level=20 if settings.log_level == "INFO" else 10
    )

    logger.debug(f"Project: {settings.project.name}")
    logger.debug(f"Region: {settings.project.aws.region}")


@app.command()
def apply(
    auto_approve: bool = typer.Option(
        False,
        "--auto-approve",
        help="Automatically approve Terraform apply"
    ),
    var_files: Optional[str] = typer.Option(
        None,
        "--var-file",
        help="Path to Terraform variable file (can be used multiple times)"
    ),
) -> None:
    """Apply infrastructure changes (Terraform only).

    This command handles Terraform operations:
    - init: Initialize Terraform
    - import: Import existing resources
    - validate: Validate configuration
    - plan: Plan changes
    - apply: Apply infrastructure

    Does NOT wait for instances or run deployments.
    Use 'deploy' command after this to configure services.
    """
    settings = get_settings()

    console.print(
        Panel(
            "[bold cyan]Cloud SOC[/bold cyan] - [yellow]Infrastructure Apply[/yellow]",
            expand=False
        )
    )

    try:
        tf_orchestrator = TerraformOrchestrator()
        logger.info("Starting Terraform infrastructure deployment...")

        tf_orchestrator.init()
        logger.info("[INIT] Terraform initialized")

        tf_orchestrator.import_all_existing_resources()
        logger.info("[IMPORT] Resources imported")

        tf_orchestrator.validate()
        logger.info("[VALIDATE] Configuration valid")

        var_file_list = [var_files] if var_files else []
        plan_file = tf_orchestrator.plan(var_files=var_file_list)
        logger.info("[PLAN] Infrastructure plan generated")

        tf_orchestrator.apply(plan_file=plan_file, auto_approve=auto_approve)
        logger.info("[APPLY] Infrastructure deployed successfully")

        console.print(
            Panel(
                "[bold green]✓ Infrastructure provisioning complete![/bold green]\n\n"
                "Next step: run [bold]cloud-soc deploy[/bold] to deploy services.\n"
                "Or run [bold]cloud-soc status[/bold] to check infrastructure status.",
                title="Cloud SOC",
                expand=False,
            )
        )

    except (TerraformStateError, OrchestrationError) as e:
        console.print(_render_error_panel(f"✗ Error: {e}"))
        raise typer.Exit(code=1)
    except Exception as e:
        logger.error(f"Unexpected error: {e}")
        console.print(_render_error_panel(f"✗ Unexpected error: {e}"))
        raise typer.Exit(code=1)


@app.command()
def deploy(
    targets: Optional[List[str]] = typer.Argument(
        None,
        help="Deployment targets (e.g., wazuh victim). Omit to deploy all."
    ),
    skip_validation: bool = typer.Option(
        False,
        "--skip-validation",
        help="Skip deployment validation"
    ),
) -> None:
    """Deploy services to instances (SSM + Playbooks).

    This command handles service deployment:
    - Waits for SSM agent readiness on instances
    - Runs deployment playbooks for specified targets
    - Validates deployment completion

    Targets can be:
    - 'wazuh' or 'wazuh_manager': Deploy Wazuh manager
    - 'victim' or 'victim_server': Deploy victim server
    - Multiple targets: 'wazuh victim' (separate each target as argument)
    - Omit all targets to deploy to all

    Requires infrastructure to be deployed first.
    """
    console.print(
        Panel(
            "[bold cyan]Cloud SOC[/bold cyan] - [yellow]Service Deployment[/yellow]",
            expand=False
        )
    )

    try:
        tf_orchestrator = TerraformOrchestrator()
        terraform_outputs = tf_orchestrator.output()

        if not terraform_outputs:
            raise OrchestrationError(
                "No Terraform outputs found. Run 'cloud-soc apply' first."
            )

        deployment_orchestrator = DeploymentOrchestrator()

        # Targets is already a list from Typer
        target_list = targets

        logger.info("Waiting for SSM agent readiness...")
        wazuh_id = terraform_outputs.get("wazuh_instance_id", {}).get("value")
        victim_id = terraform_outputs.get("victim_instance_id", {}).get("value")
        instance_ids = [id for id in [wazuh_id, victim_id] if id]

        deployment_orchestrator.wait_for_ssm_ready(instance_ids)
        logger.info("[SSM] All instances connected")

        logger.info("Starting service deployments...")
        deployment_orchestrator.deploy_targets(
            terraform_outputs,
            targets=target_list,
            skip_validation=skip_validation
        )

        if not skip_validation:
            logger.info("Validating deployment...")
            deployment_orchestrator.validate_deployment(terraform_outputs)

        console.print(
            Panel(
                "[bold green]✓ Service deployment complete![/bold green]\n\n"
                "Next step: run [bold]cloud-soc dashboard[/bold] to access the Wazuh dashboard.",
                title="Cloud SOC",
                expand=False,
            )
        )

    except OrchestrationError as e:
        console.print(_render_error_panel(f"✗ Error: {e}"))
        raise typer.Exit(code=1)
    except Exception as e:
        logger.error(f"Unexpected error: {e}")
        console.print(_render_error_panel(f"✗ Unexpected error: {e}"))
        raise typer.Exit(code=1)


@dashboard_app.callback(invoke_without_command=True)
def dashboard(
    ctx: typer.Context,
    local_port: int = typer.Option(
        8443,
        "--local-port",
        help="Local port for dashboard port forwarding"
    ),
    remote_port: int = typer.Option(
        443,
        "--remote-port",
        help="Remote dashboard port on the Wazuh instance"
    ),
    expose: bool = typer.Option(
        False,
        "--expose",
        help="Print guidance for exposing the forwarded port from the container/host environment"
    ),
) -> None:
    """Open an SSM tunnel to the Wazuh Dashboard."""
    if ctx.invoked_subcommand is not None:
        return

    console.print(
        Panel(
            "[bold cyan]Cloud SOC[/bold cyan] - [yellow]Dashboard Access[/yellow]",
            expand=False
        )
    )

    try:
        tf_orchestrator = TerraformOrchestrator()
        terraform_outputs = tf_orchestrator.output()

        if not terraform_outputs:
            raise OrchestrationError(
                "No Terraform outputs found. Run 'cloud-soc apply' first."
            )

        dashboard_orchestrator = DashboardOrchestrator()
        dashboard_orchestrator.open_tunnel(
            terraform_outputs,
            local_port=local_port,
            remote_port=remote_port,
            expose=expose,
        )
    except OrchestrationError as e:
        console.print(_render_error_panel(f"✗ Error: {e}"))
        raise typer.Exit(code=1)
    except Exception as e:
        logger.error(f"Unexpected error: {e}")
        console.print(_render_error_panel(f"✗ Unexpected error: {e}"))
        raise typer.Exit(code=1)


@dashboard_app.command("status")
def dashboard_status() -> None:
    """Query the current dashboard tunnel status."""
    console.print(
        Panel(
            "[bold cyan]Cloud SOC[/bold cyan] - [yellow]Dashboard Status[/yellow]",
            expand=False
        )
    )

    try:
        dashboard_orchestrator = DashboardOrchestrator()
        status = dashboard_orchestrator.status()

        if status.get("status") == "No active session":
            console.print(Panel("[bold yellow]No active dashboard tunnel session[/bold yellow]", expand=False))
            raise typer.Exit(code=0)

        table = Table(show_header=True, header_style="bold magenta")
        table.add_column("Property")
        table.add_column("Value")
        table.add_row("Instance ID", str(status["instance_id"]))
        table.add_row("Local Port", str(status["local_port"]))
        table.add_row("Uptime", f"{status['uptime']:.1f}s")
        table.add_row("Alive", str(status["alive"]))

        console.print(table)
    except typer.Exit:
        raise
    except Exception as e:
        logger.error(f"Unexpected error: {e}")
        console.print(_render_error_panel(f"✗ Unexpected error: {e}"))
        raise typer.Exit(code=1)


@deployment_app.command("status")
def deployment_status_command() -> None:
    """Show the latest deployment status."""
    console.print(
        Panel(
            "[bold cyan]Cloud SOC[/bold cyan] - [yellow]Deployment Status[/yellow]",
            expand=False
        )
    )

    try:
        deployment_orchestrator = DeploymentOrchestrator()
        status_data = deployment_orchestrator.get_deployment_status()

        if status_data.get("status") == "No deployment history recorded":
            console.print(Panel("[bold yellow]No deployment history found[/bold yellow]", expand=False))
            raise typer.Exit(code=0)

        deployment_table = Table(show_header=True, header_style="bold magenta")
        deployment_table.add_column("Target")
        deployment_table.add_column("Status")
        deployment_table.add_column("Started")
        deployment_table.add_column("Finished")
        deployment_table.add_column("Error")

        def format_timestamp(value: Optional[float]) -> str:
            if not value:
                return "-"
            try:
                return datetime.utcfromtimestamp(value).isoformat() + "Z"
            except Exception:
                return str(value)

        for target_name, target_data in status_data.get("targets", {}).items():
            deployment_table.add_row(
                target_name,
                str(target_data.get("status", "-")),
                format_timestamp(target_data.get("started_at")),
                format_timestamp(target_data.get("finished_at")),
                str(target_data.get("error", "")) or "-",
            )

        console.print(deployment_table)
        console.print(
            Panel(
                f"Last deployment status: [bold]{status_data.get('status')}[/bold]\n"
                f"Started: [bold]{format_timestamp(status_data.get('started_at'))}[/bold]\n"
                f"Finished: [bold]{format_timestamp(status_data.get('finished_at'))}[/bold]\n"
                f"State file: [bold]{deployment_orchestrator.deployment_state_file}[/bold]",
                expand=False,
            )
        )
    except typer.Exit:
        raise
    except Exception as e:
        console.print(_render_error_panel(f"✗ Error: {e}"))
        raise typer.Exit(code=1)


@ssm_app.command("sessions")
def ssm_sessions() -> None:
    """List active SSM sessions and instance health."""
    settings = get_settings()

    console.print(
        Panel(
            "[bold cyan]Cloud SOC[/bold cyan] - [yellow]SSM Sessions[/yellow]",
            expand=False
        )
    )

    try:
        ssm_service = SSMService(
            region=settings.project.aws.region,
            profile=settings.project.aws.profile
        )

        sessions = ssm_service.list_active_sessions()
        if not sessions:
            console.print(Panel("[bold yellow]No active SSM sessions found[/bold yellow]", expand=False))
            raise typer.Exit(code=0)

        instance_ids = [session.get("Target") for session in sessions if session.get("Target")]
        health_map = ssm_service.get_instance_health(instance_ids)

        table = Table(show_header=True, header_style="bold magenta")
        table.add_column("Session ID")
        table.add_column("Target")
        table.add_column("Status")
        table.add_column("Document")
        table.add_column("Owner")
        table.add_column("Started At")
        table.add_column("Agent Health")

        for session in sessions:
            target = session.get("Target", "-")
            health_info = health_map.get(target, {})
            agent_health = health_info.get("PingStatus", "-")
            started_at = session.get("StartDate")
            if started_at:
                started_at = str(started_at)

            table.add_row(
                str(session.get("SessionId", "-")),
                target,
                str(session.get("Status", "-")),
                str(session.get("DocumentName", "-")),
                str(session.get("Owner", "-")),
                started_at or "-",
                agent_health,
            )

        console.print(table)
    except typer.Exit:
        raise
    except Exception as e:
        console.print(_render_error_panel(f"✗ Error: {e}"))
        raise typer.Exit(code=1)


app.add_typer(dashboard_app, name="dashboard")
app.add_typer(deployment_app, name="deployment")
app.add_typer(ssm_app, name="ssm")


@app.command("import")
def import_resource(
    resource_address: str = typer.Argument(
        ...,
        help="Terraform resource address, e.g. aws_vpc.wazuh_vpc"
    ),
    resource_id: str = typer.Argument(
        ...,
        help="Existing AWS resource ID, e.g. vpc-0123456789abcdef0"
    ),
) -> None:
    """Import an existing AWS resource into Terraform state."""
    settings = get_settings()

    console.print(
        Panel(
            "[bold cyan]Cloud SOC[/bold cyan] - [yellow]Terraform Import[/yellow]",
            expand=False
        )
    )

    try:
        tf_runner = TerraformRunner(terraform_dir=settings.project.terraform.dir)
        tf_runner.init()
        tf_runner.import_resource(resource_address, resource_id)
        console.print(
            Panel(
                f"[bold green]✓ Imported {resource_address} into Terraform state[/bold green]",
                expand=False
            )
        )
    except TerraformStateError as e:
        console.print(_render_error_panel(f"✗ Error: {e}"))
        raise typer.Exit(code=1)
    except Exception as e:
        logger.error(f"Unexpected error: {e}")
        console.print(_render_error_panel(f"✗ Unexpected error: {e}"))
        raise typer.Exit(code=1)


@app.command()
def destroy(
    auto_approve: bool = typer.Option(
        False,
        "--auto-approve",
        help="Automatically approve Terraform destroy"
    ),
    force: bool = typer.Option(
        False,
        "--force",
        help="Force destroy without confirmation"
    ),
) -> None:
    """Destroy infrastructure using Terraform"""
    settings = get_settings()

    if not force:
        console.print(
            Panel(
                "[bold yellow]⚠️  WARNING: This will destroy all infrastructure![/bold yellow]",
                expand=False
            )
        )
        if not typer.confirm("Do you want to continue?"):
            console.print("[yellow]Destroy cancelled[/yellow]")
            raise typer.Exit(code=0)

    try:
        tf_runner = TerraformRunner(
            terraform_dir=settings.project.terraform.dir,
            auto_approve=auto_approve or force
        )

        logger.info("Initializing Terraform...")
        tf_runner.init()

        logger.info("Destroying infrastructure...")
        tf_runner.destroy(auto_approve=auto_approve or force)

        console.print(
            Panel(
                "[bold red]✓ Infrastructure destroyed[/bold red]",
                expand=False
            )
        )

    except TerraformStateError as e:
        console.print(_render_error_panel(f"✗ Error: {e}"))
        raise typer.Exit(code=1)
    except Exception as e:
        logger.error(f"Unexpected error: {e}")
        raise typer.Exit(code=1)


@app.command()
def status() -> None:
    """Show infrastructure status"""
    settings = get_settings()

    console.print(
        Panel(
            "[bold cyan]Cloud SOC[/bold cyan] - [yellow]Infrastructure Status[/yellow]",
            expand=False
        )
    )

    try:
        # Get AWS resources
        ec2_service = EC2Service(
            region=settings.project.aws.region,
            profile=settings.project.aws.profile
        )

        # Find VPC
        vpc = ec2_service.find_vpc(project_tag=settings.project.tag)

        if vpc:
            console.print(f"\n[bold]VPC:[/bold] {vpc.name} ({vpc.id})")
            console.print(f"  CIDR: {vpc.cidr_block}")
            console.print(f"  State: {vpc.state}")

            # Find subnets
            subnets = ec2_service.find_subnets(vpc.id)
            if subnets:
                console.print(f"\n[bold]Subnets ({len(subnets)}):[/bold]")
                table = Table(title="Subnets")
                table.add_column("Name", style="cyan")
                table.add_column("ID", style="magenta")
                table.add_column("CIDR", style="green")
                table.add_column("AZ", style="yellow")

                for subnet in subnets:
                    table.add_row(subnet.name, subnet.id, subnet.cidr_block, subnet.availability_zone)

                console.print(table)

            # Find instances
            instances = ec2_service.find_instances(vpc_id=vpc.id, project_tag=settings.project.tag)
            if instances:
                console.print(f"\n[bold]Instances ({len(instances)}):[/bold]")
                table = Table(title="EC2 Instances")
                table.add_column("Name", style="cyan")
                table.add_column("ID", style="magenta")
                table.add_column("Type", style="green")
                table.add_column("State", style="yellow")
                table.add_column("IP", style="blue")

                for instance in instances:
                    name = instance.tags.get("Name", "-")
                    ip = instance.public_ip or instance.private_ip or "-"
                    table.add_row(name, instance.id, instance.type, instance.state, ip)

                console.print(table)
        else:
            console.print("[yellow]No VPC found[/yellow]")

    except Exception as e:
        console.print(f"[red]Error: {e}[/red]")
        raise typer.Exit(code=1)


@app.command()
def validate() -> None:
    """Validate Terraform configuration"""
    settings = get_settings()

    try:
        tf_runner = TerraformRunner(terraform_dir=settings.project.terraform.dir)
        tf_runner.init()
        tf_runner.validate()
        console.print("[bold green]✓ Configuration is valid[/bold green]")
    except TerraformStateError as e:
        console.print(f"[bold red]✗ Validation failed: {e}[/bold red]")
        raise typer.Exit(code=1)


@app.command()
def version() -> None:
    """Show version information"""
    from cloudsoc import __version__
    console.print(f"[bold cyan]Cloud SOC[/bold cyan] version [yellow]{__version__}[/yellow]")


# Create __init__.py for package
if __name__ == "__main__":
    app()
