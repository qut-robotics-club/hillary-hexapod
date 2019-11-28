#!/bin/bash
conda create --name qutrc -f environment.yml
cd hyper_controller/control_server && npm i
