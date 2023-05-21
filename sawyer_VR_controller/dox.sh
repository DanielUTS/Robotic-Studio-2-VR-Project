#!/bin/bash

while true; do
  # Run the 'doxygen Doxyfile' command
  doxygen Doxyfile

  # Delay between consecutive runs (in seconds)
  sleep 5
done

