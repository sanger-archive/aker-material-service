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

# Add the wait-for-it file to utils
ADD https://raw.githubusercontent.com/vishnubob/wait-for-it/master/wait-for-it.sh /utils/wait-for-it.sh
RUN chmod u+x /utils/wait-for-it.sh

# Run the app
CMD python run.py
