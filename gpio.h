#ifndef _GPIO_H_
#define _GPIO_H_

#define HIGH 1
#define LOW  0

#define OUTPUT 1
#define INPUT  0

void set_gpio_mode(int pin,int mode);
int get_gpio_pin(int pin);
void set_gpio_pin(int pin,int level);

#endif /* _GPIO_H_ */
