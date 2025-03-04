# Medical Arena





## Deploy on AWS Lightsail

### Build the image locally
First build the image on local machine:
'''
docker build -t medical_arena_image .
docker save -o medical_arena_image.tar medical_arena_image
'''

Then scp it to the lightsail intance.

### Install the docker on lightsail instance

Install the docker on lightsail instance (if docker is not installed):
'''
sudo apt-get update
sudo apt-get install apt-transport-https ca-certificates curl gnupg lsb-release
curl -fsSL https://download.docker.com/linux/ubuntu/gpg | sudo gpg --dearmor -o /usr/share/keyrings/docker-archive-keyring.gpg
echo \
  "deb [arch=$(dpkg --print-architecture) signed-by=/usr/share/keyrings/docker-archive-keyring.gpg] https://download.docker.com/linux/ubuntu \
  $(lsb_release -cs) stable" | sudo tee /etc/apt/sources.list.d/docker.list > /dev/null
sudo apt-get update
sudo apt-get install docker-ce docker-ce-cli containerd.io
sudo usermod -aG docker $USER
'''



Load the image one lightsail instance:
'''
docker load -i medical_arena_image.tar
'''

Run it:
'''
docker run -d -p 5000:5000 medical_arena_image