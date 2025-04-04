# Driver layer personal development code

This is my personal development code for driver learning

# Content

## CharDevice
Create a string device at the driver layer and call it at application layer.
which is in /dev/mychar_dev

## DevicetreeGpio
Create a devicetree node in .dts, define gpio property.
In driver code, match this node, and request gpio irq.
In machine, add a py code send high signal to gpio 55, we can observe that have entered the interrupt registration function