FROM zenika/terraform-aws-cli:release-3.7_terraform-0.13.1_awscli-1.17.17
# FROM python:3.7-alpine
# WORKDIR /code
# ENV FLASK_APP app.py
# ENV FLASK_RUN_HOST 0.0.0.0
# RUN apk add --no-cache gcc musl-dev linux-headers bash
# RUN curl -fsSL https://apt.releases.hashicorp.com/gpg | apt-key add -
# RUN apt-add-repository "deb [arch=amd64] https://apt.releases.hashicorp.com $(lsb_release -cs) main"
# RUN apt-get update && apt-get install terraform
# COPY requirements.txt requirements.txt
# RUN pip install -r requirements.txt
# EXPOSE 5000
RUN apt-get update
RUN apt-get install -y rubygems postgresql postgresql-contrib python3-pip
RUN pip3 install click
RUN gem install terraform_landscape
COPY . .
# CMD ["flask", "run"]
ENTRYPOINT ["tail", "-f", "/dev/null"]