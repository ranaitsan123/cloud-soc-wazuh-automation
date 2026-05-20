"""Main CLI entry point using Typer"""

from pathlib import Path
from typing import Optional
import typer
from rich.console import Console
from rich.panel import Panel
from rich.table import Table

from cloudsoc.config.settings import get_settings
from cloudsoc.terraform.runner import TerraformRunner, TerraformStateError
from cloudsoc.aws.ec2 import EC2Service
from cloudsoc.orchestrator import DeploymentOrchestrator, OrchestrationError
from cloudsoc.utils.logger import logger, setup_logger

app = typer.Typer(help="Cloud SOC Infrastructure Orchestration Platform")
console = Console()


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
    """Apply infrastructure changes using Terraform"""
    settings = get_settings()

    console.print(
        Panel(
            "[bold cyan]Cloud SOC[/bold cyan] - [yellow]Infrastructure Apply[/yellow]",
            expand=False
        )
    )

    try:
        orchestrator = DeploymentOrchestrator()
        logger.info("Starting deployment orchestration...")
        var_file_list = [var_files] if var_files else []
        orchestrator.apply(auto_approve=auto_approve, var_files=var_file_list)

    except (TerraformStateError, OrchestrationError) as e:
        console.print(Panel(f"[bold red]✗ Error: {e}[/bold red]", expand=False))
        raise typer.Exit(code=1)
    except Exception as e:
        logger.error(f"Unexpected error: {e}")
        console.print(Panel(f"[bold red]✗ Unexpected error: {e}[/bold red]", expand=False))
        raise typer.Exit(code=1)


@app.command()
def dashboard(
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
) -> None:
    """Open an SSM tunnel to the Wazuh Dashboard."""
    console.print(
        Panel(
            "[bold cyan]Cloud SOC[/bold cyan] - [yellow]Dashboard Access[/yellow]",
            expand=False
        )
    )

    try:
        orchestrator = DeploymentOrchestrator()
        orchestrator.open_dashboard(local_port=local_port, remote_port=remote_port)
    except OrchestrationError as e:
        console.print(Panel(f"[bold red]✗ Error: {e}[/bold red]", expand=False))
        raise typer.Exit(code=1)
    except Exception as e:
        logger.error(f"Unexpected error: {e}")
        console.print(Panel(f"[bold red]✗ Unexpected error: {e}[/bold red]", expand=False))
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
        console.print(Panel(f"[bold red]✗ Error: {e}[/bold red]", expand=False))
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
