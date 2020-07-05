class RollBackException(Exception):
    # 在原子事务中抛出该错误, 表示要求数据库进行回滚
    pass


class OldRefreshTokenException(Exception):
    # 抛出该错误, 表示客户端并发请求时拿着原refresh_token来请求, 给予放行, 去刷新token
    pass