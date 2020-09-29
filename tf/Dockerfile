FROM zenika/terraform-aws-cli:release-3.7_terraform-0.13.1_awscli-1.17.17
RUN apt-get update
RUN apt-get install -y rubygems postgresql-client python3-pip
RUN pip3 install boto3 click ipython
RUN gem install terraform_landscape
RUN gem install terraforming
COPY . .
# CMD ["flask", "run"]
ENTRYPOINT ["tail", "-f", "/dev/null"]