# Auto Stream Writer
Automatically record shows from internet radio 

## Installation
- make sure you have docker installed and the service enabled
- copy your rclone config to recorder/rclone.conf
- add your stream url and rclone drive name to docker-compose.yaml
- `# docker-compose build`
- `# docker-compose up -d`

## Usage
- go to localhost:5000
- add names of hosts first
- then add the shows
- they'll record to the recordings folder (will be created) and upload to google drive
- enjoy :3
