"""SSM service for AWS interactions"""

from typing import Optional, List, Dict, Any
import boto3
from botocore.exceptions import ClientError
from cloudsoc.utils.logger import logger


class SSMService:
    """Service for AWS Systems Manager operations using Boto3"""

    def __init__(self, region: str = "eu-north-1", profile: Optional[str] = None):
        """
        Initialize SSM service.

        Args:
            region: AWS region
            profile: AWS profile name
        """
        session = boto3.Session(profile_name=profile) if profile else boto3.Session()
        self.client = session.client("ssm", region_name=region)
        self.region = region
        self.logger = logger

    def send_command(
        self,
        instance_ids: List[str],
        commands: List[str],
        working_directory: str = "",
        timeout: int = 3600,
        document_name: str = "AWS-RunShellScript"
    ) -> Optional[str]:
        """
        Send command to EC2 instances via SSM.

        Args:
            instance_ids: List of instance IDs
            commands: List of shell commands to execute
            working_directory: Working directory for commands
            timeout: Command timeout in seconds
            document_name: SSM document to use

        Returns:
            Command ID or None if failed
        """
        try:
            kwargs = {
                "InstanceIds": instance_ids,
                "DocumentName": document_name,
                "Parameters": {"commands": commands},
                "TimeoutSeconds": timeout
            }

            if working_directory:
                kwargs["Parameters"]["workingDirectory"] = [working_directory]

            response = self.client.send_command(**kwargs)
            command_id = response["Command"]["CommandId"]

            self.logger.info(f"✓ Sent command {command_id} to {len(instance_ids)} instances")
            return command_id

        except ClientError as e:
            self.logger.error(f"Failed to send command: {e}")
            return None

    def get_command_invocation(
        self,
        command_id: str,
        instance_id: str
    ) -> Optional[Dict[str, Any]]:
        """
        Get command invocation details.

        Args:
            command_id: Command ID
            instance_id: Instance ID

        Returns:
            Command invocation details or None
        """
        try:
            response = self.client.get_command_invocation(
                CommandId=command_id,
                InstanceId=instance_id
            )

            return {
                "status": response.get("Status"),
                "output": response.get("StandardOutputContent", ""),
                "error": response.get("StandardErrorContent", ""),
                "return_code": response.get("ResponseCode", -1)
            }

        except ClientError as e:
            error_code = e.response.get("Error", {}).get("Code")
            if error_code == "InvocationDoesNotExist":
                self.logger.debug(
                    f"SSM invocation not yet available for command {command_id} on instance {instance_id}."
                )
                return {
                    "status": "Pending",
                    "output": "",
                    "error": "",
                    "return_code": -1
                }

            self.logger.error(f"Failed to get command invocation: {e}")
            return None

    def wait_for_command(
        self,
        command_id: str,
        instance_id: str,
        timeout: int = 120,
        poll_interval: int = 5
    ) -> Optional[Dict[str, Any]]:
        """
        Wait for an SSM command invocation to complete.

        Args:
            command_id: Command ID
            instance_id: Instance ID
            timeout: Timeout in seconds
            poll_interval: Polling interval in seconds

        Returns:
            Command invocation result or None
        """
        import time

        start_time = time.time()
        while time.time() - start_time < timeout:
            invocation = self.get_command_invocation(command_id, instance_id)
            if invocation is None:
                return None

            status = invocation.get("status")
            if status in ["Success", "Failed", "Cancelled", "TimedOut"]:
                return invocation
            if status in ["Pending", "InProgress", "Delayed"]:
                self.logger.info(f"Waiting for SSM command {command_id} to complete...")
                time.sleep(poll_interval)
                continue

            self.logger.debug(f"Received unexpected SSM status '{status}' for command {command_id}")
            time.sleep(poll_interval)

        self.logger.warning(f"SSM command {command_id} did not complete within {timeout} seconds")
        return None

    def put_parameter(
        self,
        name: str,
        value: str,
        param_type: str = "String",
        description: str = "",
        overwrite: bool = True,
        tags: Optional[Dict[str, str]] = None
    ) -> bool:
        """
        Create or update SSM parameter.

        Args:
            name: Parameter name
            value: Parameter value
            param_type: Type (String, StringList, SecureString)
            description: Parameter description
            overwrite: Overwrite if exists
            tags: Tags to attach

        Returns:
            True if successful
        """
        try:
            kwargs = {
                "Name": name,
                "Value": value,
                "Type": param_type,
                "Overwrite": overwrite
            }

            if description:
                kwargs["Description"] = description

            if tags:
                kwargs["Tags"] = [{"Key": k, "Value": v} for k, v in tags.items()]

            self.client.put_parameter(**kwargs)
            self.logger.info(f"✓ Created/updated parameter: {name}")
            return True

        except ClientError as e:
            self.logger.error(f"Failed to put parameter {name}: {e}")
            return False

    def get_parameter(self, name: str, with_decryption: bool = False) -> Optional[str]:
        """
        Get SSM parameter value.

        Args:
            name: Parameter name
            with_decryption: Decrypt SecureString parameters

        Returns:
            Parameter value or None
        """
        try:
            response = self.client.get_parameter(
                Name=name,
                WithDecryption=with_decryption
            )

            return response["Parameter"]["Value"]

        except ClientError as e:
            self.logger.error(f"Parameter not found: {name}")
            return None

    def wait_for_instance(
        self,
        instance_id: str,
        timeout: int = 600,
        poll_interval: int = 15
    ) -> bool:
        """Wait until the SSM agent is online for the target instance."""
        import time

        start_time = time.time()

        while time.time() - start_time < timeout:
            try:
                response = self.client.describe_instance_information(
                    Filters=[
                        {
                            "Key": "InstanceIds",
                            "Values": [instance_id]
                        }
                    ]
                )
                instances = response.get("InstanceInformationList", [])

                if instances and instances[0].get("PingStatus") == "Online":
                    self.logger.info(f"✓ SSM is online for instance {instance_id}")
                    return True

            except ClientError as e:
                self.logger.debug(f"SSM instance information read failed: {e}")

            self.logger.info(f"Waiting for SSM readiness for {instance_id}...")
            time.sleep(poll_interval)

        self.logger.warning(f"SSM did not become ready for instance {instance_id} within {timeout} seconds")
        return False

    def list_active_sessions(
        self,
        state: str = "Active",
        max_results: int = 50,
    ) -> Optional[List[Dict[str, Any]]]:
        """
        List active SSM sessions.

        Args:
            state: Session state to filter by (default: Active)
            max_results: Maximum number of sessions to return

        Returns:
            List of session dictionaries or None if failed
        """
        try:
            response = self.client.describe_sessions(
                State=state,
                MaxResults=max_results,
            )
            return response.get("Sessions", [])
        except ClientError as e:
            self.logger.error(f"Failed to list SSM sessions: {e}")
            return None

    def get_instance_health(
        self,
        instance_ids: List[str],
    ) -> Dict[str, Dict[str, Any]]:
        """
        Get health information for SSM-managed instances.

        Args:
            instance_ids: List of EC2 instance IDs

        Returns:
            Mapping of instance ID to health information
        """
        if not instance_ids:
            return {}

        try:
            response = self.client.describe_instance_information(
                Filters=[
                    {
                        "Key": "InstanceIds",
                        "Values": instance_ids,
                    }
                ]
            )

            results: Dict[str, Dict[str, Any]] = {}
            for instance in response.get("InstanceInformationList", []):
                results[instance.get("InstanceId")] = {
                    "PingStatus": instance.get("PingStatus"),
                    "PlatformType": instance.get("PlatformType"),
                    "IPAddress": instance.get("IPAddress"),
                    "ComputerName": instance.get("ComputerName"),
                }
            return results
        except ClientError as e:
            self.logger.error(f"Failed to get instance health: {e}")
            return {}

    def delete_parameter(self, name: str) -> bool:
        """
        Delete SSM parameter.

        Args:
            name: Parameter name

        Returns:
            True if successful
        """
        try:
            self.client.delete_parameter(Name=name)
            self.logger.info(f"✓ Deleted parameter: {name}")
            return True

        except ClientError as e:
            self.logger.error(f"Failed to delete parameter {name}: {e}")
            return False

    def start_port_forward(
        self,
        instance_id: str,
        local_port: int,
        remote_port: int
    ) -> Optional[str]:
        """
        Start port forwarding session via SSM.

        Args:
            instance_id: EC2 instance ID
            local_port: Local port
            remote_port: Remote port on instance

        Returns:
            Session ID or None if failed
        """
        try:
            response = self.client.start_session(
                Target=instance_id,
                DocumentName="AWS-StartPortForwardingSession",
                Parameters={
                    "portNumber": [str(remote_port)],
                    "localPortNumber": [str(local_port)]
                }
            )

            session_id = response["SessionId"]
            self.logger.info(
                f"✓ Started port forward: localhost:{local_port} -> {instance_id}:{remote_port}"
            )
            return session_id

        except ClientError as e:
            self.logger.error(f"Failed to start port forward: {e}")
            return None
