
ansible-playbook develop.yml \
  -i raspi-host \
  -u pi \
  --ask-pass \
  -e 'ansible_python_interpreter=/usr/bin/python3'