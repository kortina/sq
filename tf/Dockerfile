FROM zenika/terraform-aws-cli:release-3.7_terraform-0.13.1_awscli-1.17.17
RUN apt-get update
RUN apt-get install -y rubygems postgresql postgresql-contrib python3-pip
RUN pip3 install click
RUN gem install terraform_landscape
COPY . .
# CMD ["flask", "run"]
ENTRYPOINT ["tail", "-f", "/dev/null"]