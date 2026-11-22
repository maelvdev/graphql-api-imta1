FROM python:3.14-slim

WORKDIR /app

# copy the requirements file in the workdir
COPY requirements.txt .

# install the Python requirements
RUN pip install -r requirements.txt

# copy the app files and directories
COPY . .

EXPOSE 3001

# start movie.py when the container is started
ENTRYPOINT ["python", "movie.py"]
