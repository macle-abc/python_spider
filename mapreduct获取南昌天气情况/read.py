from spider.item import NanChangTemperature


def main():
    for item in NanChangTemperature.objects:
        print(item.date, item.max_temperature)


if __name__ == '__main__':
    main()
