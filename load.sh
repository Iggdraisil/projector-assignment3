#!/bin/bash
siege -t 10m -c 100 http://localhost:8082/test
