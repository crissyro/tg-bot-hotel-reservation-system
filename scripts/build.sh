#!/bin/bash

set -e

echo -e "\033[1;34mЗапуск сборки проекта...\033[0m"
cd bot && docker compose up -d --build
echo -e "\033[1;32mКонтейнеры успешно собраны и запущены!\033[0m"