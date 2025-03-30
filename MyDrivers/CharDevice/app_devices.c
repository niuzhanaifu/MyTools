#include <stdio.h>
#include <stdlib.h>
#include <fcntl.h>
#include <unistd.h>
#include <sys/ioctl.h>
#include <errno.h>
#include <unistd.h>
#include <string.h>
#include <dirent.h>
#include "test_devices.h"

#define BUFFER_SIZE 1024
static my_test_devices_t data = {0};
int main() {
    int log_fd;
    char buffer[BUFFER_SIZE] = {0};

    log_fd = open(TEST_LOG_FILE, O_WRONLY | O_APPEND | O_CREAT, 0644);
    if (log_fd == -1) {
        printf("open %s failed. result: %s", TEST_LOG_FILE, strerror(errno));
        return -1;
    }
    int fd;

    fd = open("/dev/mychar_dev", O_RDWR);
    if (fd == -1) {
        printf("unable open file %s, res:%s", "/dev/mychar_dev", strerror(errno));
        return -1;
    }

    int ret = ioctl(fd, MY_GET_VALUE, &data);
    if (ret == -1) {
        printf("ioctl failed, result:%s", strerror(errno));
        close(fd);
        return -1;
    }

    const char *message = "data message:\n";
    ssize_t bytes_written = 0;
    bytes_written = write(log_fd, message, strlen(message));
    snprintf(buffer, BUFFER_SIZE, "%d.\n", data.count);
    bytes_written = write(log_fd, buffer, strlen(buffer));

    close(fd);
    close(log_fd);

    return 0;
}