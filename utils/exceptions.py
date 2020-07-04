class RollBackException(Exception):
    # 在原子事务中抛出该错误, 表示要求数据库进行回滚
    pass
