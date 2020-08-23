from mrjob.job import MRJob


class MRMax(MRJob):
    def mapper(self, key, value):
        "2018-12-30 -1"
        result = value.split()
        if len(result) != 2:
            print("格式错误!")
        else:
            date, c = result
            yield date[:7], int(c)

    def reducer(self, key, values):
        yield key, max(values)


if __name__ == '__main__':
    MRMax.run()
