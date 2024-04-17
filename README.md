# Zwift smart fan controller


# Installation

- `pip3 install openant`

# Environment variables

- 

# Configure startup on boot

- Copy the file [zwift-fan.service](zwift-fan.service).

```bash
sudo cp zwift-fan.service /etc/systemd/system/zwift-fan.service
```

- Edit the file and adapt the path to the entry point python script

```bash
sudo nano /etc/systemd/system/zwift-fan.service
```

- Reload systemd manager configuration:

```bash
sudo systemctl daemon-reload
```

- Enable the service to start on boot:

```bash
sudo systemctl enable zwift-fan.service
```

- Start the service:

```bash
sudo systemctl start zwift-fan.service
```

- Check the status to ensure it's running:

```bash
sudo systemctl status zwift-fan.service
```