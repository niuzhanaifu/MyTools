#include <linux/init.h>
#include <linux/module.h>
#include <linux/fs.h>
#include <linux/uaccess.h>
#include <linux/kernel.h>
#include <linux/cdev.h>
#include <linux/device.h>
#include <linux/ioctl.h>
#include <stdbool.h>

// 定义设备名称
#define DEVICE_NAME "mychar_dev"
// 定义缓冲区大小
#define BUFFER_SIZE 1024

// 设备的主设备号
static dev_t dev_num;
// 字符设备结构体
static struct cdev cdev;
// 设备类
static struct class *dev_class;
// 内核缓冲区
static char buffer[BUFFER_SIZE];
// 缓冲区当前长度
static int buffer_length = 0;
// struct define
typedef struct {
    uint16_t tag;
} my_test_devices_t, *my_test_devices_handle_t;
typedef struct {
    uint16_t count;
} my_test_data_t;
static my_test_data_t data = {0};
// 定义的IO操作函数
#define MY_CHAR_DEVICE 'c'
#define MY_GET_VALUE _IOWR(MY_CHAR_DEVICE, 1, my_test_devices_handle_t)
#define MY_SET_VALUE _IOWR(MY_CHAR_DEVICE, 2, my_test_devices_handle_t)

long mychar_ioctl(struct file *filp, unsigned int cmd, unsigned long arg) {
    switch (cmd)
    {
    case MY_GET_VALUE:
        data.count++;
        if (copy_to_user((void *)arg, &data, sizeof(data))) {
            return -EFAULT;
        }
        break;

    default:
        break;
    }
    return 0;
}

static int mychar_open(struct inode *inode, struct file *file) {
    printk(KERN_INFO "mychar_dev: Device opened\n");
    return 0;
}

static int mychar_release(struct inode *inode, struct file *file) {
    printk(KERN_INFO "mychar_dev: Device closed\n");
    return 0;
}

static ssize_t mychar_read(struct file *file, char __user *buf, size_t count, loff_t *f_pos) {
    int bytes_to_read;

    if (*f_pos >= buffer_length) {
        return 0;
    }
    if (*f_pos + count > buffer_length) {
        bytes_to_read = buffer_length - *f_pos;
    } else {
        bytes_to_read = count;
    }

    if (copy_to_user(buf, buffer + *f_pos, bytes_to_read)) {
        return -EFAULT;
    }

    *f_pos += bytes_to_read;

    return bytes_to_read;
}

static ssize_t mychar_write(struct file *file, const char __user *buf, size_t count, loff_t *f_pos) {
    int bytes_to_write;

    if (*f_pos + count > BUFFER_SIZE) {
        bytes_to_write = BUFFER_SIZE - *f_pos;
    } else {
        bytes_to_write = count;
    }

    if (copy_from_user(buffer + *f_pos, buf, bytes_to_write)) {
        return -EFAULT;
    }

    if (*f_pos + bytes_to_write > buffer_length) {
        buffer_length = *f_pos + bytes_to_write;
    }
    *f_pos += bytes_to_write;

    return bytes_to_write;
}

static struct file_operations fops = {
    .owner = THIS_MODULE,
    .open = mychar_open,
    .release = mychar_release,
    .read = mychar_read,
    .write = mychar_write,
    .unlocked_ioctl = mychar_ioctl,
};

static int __init mychar_init(void) {
    int ret;

    // alloc device number
    ret = alloc_chrdev_region(&dev_num, 0, 1, DEVICE_NAME);
    if (ret < 0) {
        printk(KERN_ERR "mychar_dev: Failed to allocate major number\n");
        return ret;
    }
    printk(KERN_INFO "mychar_dev: Major number allocated: %d\n", MAJOR(dev_num));

    // init char devices
    cdev_init(&cdev, &fops);
    cdev.owner = THIS_MODULE;

    // add char device to kernel
    ret = cdev_add(&cdev, dev_num, 1);
    if (ret < 0) {
        printk(KERN_ERR "mychar_dev: Failed to add cdev\n");
        unregister_chrdev_region(dev_num, 1);
        return ret;
    }

    // create class, /sys/class/{$DEVICE_NAME}
    dev_class = class_create(THIS_MODULE, DEVICE_NAME);
    if (IS_ERR(dev_class)) {
        printk(KERN_ERR "mychar_dev: Failed to create device class\n");
        cdev_del(&cdev);
        unregister_chrdev_region(dev_num, 1);
        return PTR_ERR(dev_class);
    }

    // /dev/{$DEVICE_NAME}
    device_create(dev_class, NULL, dev_num, NULL, DEVICE_NAME);
    printk(KERN_INFO "mychar_dev: Device created successfully\n");

    data.count = 3;
    return 0;
}

static void __exit mychar_exit(void) {

    device_destroy(dev_class, dev_num);

    class_destroy(dev_class);

    cdev_del(&cdev);

    unregister_chrdev_region(dev_num, 1);
    printk(KERN_INFO "mychar_dev: Device removed successfully\n");
}

module_init(mychar_init);
module_exit(mychar_exit);

MODULE_LICENSE("GPL");
MODULE_AUTHOR("niuzhanaifu");
MODULE_DESCRIPTION("A simple character device driver");