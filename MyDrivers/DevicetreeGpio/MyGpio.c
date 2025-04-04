#include <linux/gpio.h>
#include <linux/of_gpio.h>
#include <linux/of.h>
#include <linux/platform_device.h>
#include <linux/of_device.h>
#include <linux/init.h>
#include <linux/kernel.h>
#include <linux/module.h>
#include <linux/interrupt.h>

struct device_node *mydevice_node;
int gpio_pin;
int irq_num;
int ret;

#define LOGTAG "MyGpio"

static irqreturn_t my_irq_handler(int irq, void *dev_id)
{
    printk(LOGTAG"Interrupt %d occurred!\n", irq);
    return IRQ_HANDLED;
}

int my_probe(struct platform_device *platform_dev) {
    printk(LOGTAG"This is my gpio node");

	mydevice_node = platform_dev->dev.of_node;
    gpio_pin = of_get_named_gpio(platform_dev->dev.of_node, "gpios", 0);
    printk(LOGTAG"my gpio pin:%d", gpio_pin);

	if (gpio_is_valid(gpio_pin)) {
		printk(LOGTAG"gpio num %d is valid", gpio_pin);
	} else {
		printk(LOGTAG"gpio num %d is invalid", gpio_pin);
		return -1;
	}
	ret = devm_gpio_request(&platform_dev->dev, gpio_pin, "my_gpio");
	if (ret) {
		printk(LOGTAG"Failed to request gpio %d, ret: %d", gpio_pin, ret);
		return ret;
	}

	ret = gpio_direction_input(gpio_pin);
    if (ret) {
        printk(LOGTAG"Failed to set GPIO %d as input: %d\n", gpio_pin, ret);
        goto gpio_free;
    }

	irq_num = gpio_to_irq(gpio_pin);
	if (irq_num < 0) {
		printk(LOGTAG"gpio to irq failed, irq_num:%d", irq_num);
		goto gpio_free;
	} else {
		printk(LOGTAG"gpio to irq success, irq_num:%d", irq_num);
	}

	ret = devm_request_irq(&platform_dev->dev, irq_num, my_irq_handler, IRQF_TRIGGER_RISING, "my_irq", NULL);
	if (ret < 0) {
		printk(LOGTAG"devm_request_irq failed");
		goto gpio_free;
	} else {
		printk(LOGTAG"devm_request_irq success");
	}
	return 0;

gpio_free:
	devm_gpio_free(&platform_dev->dev, gpio_pin);
    return ret;
}


//驱动中匹配设备树
static const struct of_device_id my_match[] = {
	{ .compatible = "my_device_tree"},
	{},
};

static struct platform_driver my_platform_driver = {
	.probe		= my_probe,
	.driver		= {
		.name	= "my_device_tree",
		.of_match_table = my_match,
	},
};

static int __init my_driver_init(void)
{
    return platform_driver_register(&my_platform_driver);
}

static void __exit my_driver_exit(void)
{
    platform_driver_unregister(&my_platform_driver);
}

module_init(my_driver_init);
module_exit(my_driver_exit);

MODULE_LICENSE("GPL");
MODULE_AUTHOR("LiHao");
MODULE_DESCRIPTION("A simple example module");
