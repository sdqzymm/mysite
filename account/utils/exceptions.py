class RollBackException(Exception):
    # 注册视图中抛出该错误, 表示创建用户失败, 数据库回滚
    pass


class OldRefreshTokenException(Exception):
    # 抛出该错误, 表示客户端并发请求时拿着原refresh_token来请求, 给予放行, 去刷新token
    pass