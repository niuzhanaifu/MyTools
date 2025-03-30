#ifndef MY_DEVICE
#define MY_DEVICE

#include <stdint.h>

typedef struct {
    uint16_t count;
} my_test_devices_t, *my_test_devices_handle_t;

#define MY_CHAR_DEVICE 'c'
#define MY_GET_VALUE _IOWR(MY_CHAR_DEVICE, 1, my_test_devices_handle_t)
#define MY_SET_VALUE _IOWR(MY_CHAR_DEVICE, 2, my_test_devices_handle_t)

#define TEST_LOG_FILE "/tmp/my_test_dir/test_log"

#define KMSG_DEVICE "/dev/kmsg"
#define KMSG_OUTPUT_DIR "/tmp/my_test_dir"
#define KMSG_OUTPUT_FILE "/tmp/my_test_dir/kmsg_output.log"

#endif