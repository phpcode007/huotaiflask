import re


class ExceptionUtilSingleton(object):

    def json_errer_message(self, error):

        #判断是不是空白参数异常
        #None is not of type
        if 'None is not of type' in error:
            return '空白参数'

        # Failed validating 'pattern' in schema['properties']['username']:
        # {'description': '用户名只能小写字母和数字(不能大写)，不能使用特殊字符,长度是30',
        #  'errorMessage': '错误信息111111111111',
        #  'pattern': '^[a-z0-9]{1,30}$',
        #  'type': 'string'}

        #用正则表达式，提取上面的错误信息，返回中文错误信息
        result = re.findall(r"'description': '(.*)'", str(error))

        #['用户名只能小写字母和数字(不能大写)，不能使用特殊字符,长度是30']
        #进行第二次进行提取
        two_result =  re.findall(r"'(.*)'", result)

        print('错误信息...................................')
        # print(two_result)

        # if not two_result:
        #     return '空白参数'

        return two_result

ExceptionUtil = ExceptionUtilSingleton()