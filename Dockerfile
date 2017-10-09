# aker-materials-service
# Use python 2.7
FROM python:2.7

# Create the working directory
# https://docs.docker.com/engine/reference/builder/#workdir
WORKDIR /code

# Add the required packages
ADD requirements.txt /code/

# Install the required packages
RUN pip install -r requirements.txt

# Add all remaining contents to the image
ADD . /code

# Run the app
CMD python run.py
