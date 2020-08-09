# -*- mode: ruby -*-
# vi: set ft=ruby :

Vagrant.configure("2") do |config|

  config.vm.box = "bento/ubuntu-18.04"
  config.vm.hostname = 'ansible'
  config.vm.synced_folder "./ansible_lib", "/ansible_lib"
  config.vm.provider "virtualbox" do |vbox|
    vbox.gui = false
    vbox.cpus = 2
    vbox.memory = 2048
  end
  config.vm.provision "shell", inline: <<-SHELL
    apt-get update
    apt-get install -y python3-pip sshpass
    pip3 install ansible
    apt-get upgrade -y
  SHELL
end
