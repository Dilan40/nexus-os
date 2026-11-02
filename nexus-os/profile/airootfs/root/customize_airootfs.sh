#!/usr/bin/env bash
set -euo pipefail

mkdir -p /etc/systemd/system/getty@tty1.service.d
cat > /etc/systemd/system/getty@tty1.service.d/autologin.conf <<EOF
[Service]
ExecStart=
ExecStart=-/sbin/agetty --autologin root --noclear %I \$TERM
EOF

mkdir -p /var/lib/nexus/bridge/{cmd,resp}
chmod 777 /var/lib/nexus/bridge/{cmd,resp}
echo "3.0.0" > /etc/nexus-version

systemctl enable NetworkManager
systemctl enable seatd
systemctl enable kiosk.service
systemctl enable nexus-bridge
systemctl enable nexus-bridge-handler
systemctl enable nexus-update-check.timer
systemctl set-default graphical.target

echo "nexus" > /etc/hostname
rm -rf /var/cache/pacman/pkg/*