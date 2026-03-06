FROM rockylinux:9-minimal

# Install base utilities
RUN microdnf install -y \
    unzip \
    git \
    curl \
    jq \
    python3 \
    python3-pip \
    zsh \
    nmap \
    hydra \
    && microdnf clean all

# Install AWS CLI v2
RUN curl "https://awscli.amazonaws.com/awscli-exe-linux-x86_64.zip" -o "awscliv2.zip" && \
    unzip awscliv2.zip && \
    ./aws/install && \
    rm -rf aws awscliv2.zip

# Install Terraform (latest version dynamically)
RUN LATEST_VERSION=$(curl -s https://api.github.com/repos/hashicorp/terraform/releases/latest | jq -r '.tag_name' | sed 's/v//') && \
    curl -O "https://releases.hashicorp.com/terraform/${LATEST_VERSION}/terraform_${LATEST_VERSION}_linux_amd64.zip" && \
    unzip terraform_${LATEST_VERSION}_linux_amd64.zip -d /usr/local/bin && \
    rm terraform_${LATEST_VERSION}_linux_amd64.zip

# Install Python libraries for AWS automation
RUN pip3 install --no-cache-dir boto3

WORKDIR /workspace