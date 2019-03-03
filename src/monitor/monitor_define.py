
#监控器注册库
#原则上应该使用SQL数据库来进行存储，这里为了简单，使用MongoDB存储

MONITOR_DEFINE = {
    '044A02':{
        'ID':'044A02',
        'NAME':'上隅角测点瓦斯浓度', #名称
        'TYPE':'CH4',
        'UNIT':'%', # 单位
        'POS':{
            'LON_LAT':[], # 坐标
            'WF':'W15117', #工作面
            'TEXT':'W15117工作面上隅角', # 描述
        }, # 位置
    },

    '044A03':{
        'ID':'044A03',
        'NAME':'回风测点瓦斯浓度', #名称
        'TYPE':'CH4',
        'UNIT':'%', # 单位
        'POS':{
            'LON_LAT':[], # 坐标
            'WF':'W15117', #工作面
            'TEXT':'W15117工作面回风处', # 描述
        }, # 位置
    },
    
    '009A13':{
        'ID':'009a13',
        'NAME':'进风测点瓦斯浓度', #名称
        'TYPE':'CH4',
        'UNIT':'%', # 单位
        'POS':{
            'LON_LAT':[], # 坐标
            'WF':'W15117', #工作面
            'TEXT':'W15117工作面上进风处', # 描述
        }, # 位置
    },

    '044A11':{
        'ID':'044A11',
        'NAME':'回风混合测点瓦斯浓度', #名称
        'TYPE':'CH4',
        'UNIT':'%', # 单位
        'POS':{
            'LON_LAT':[], # 坐标
            'WF':'W15117', #工作面
            'TEXT':'W15117工作面回风混合', # 描述
        }, # 位置
    },

    '044A15':{
        'ID':'044A15',
        'NAME':'工作面风速', #名称
        'TYPE':'AIR_SPEED',
        'UNIT':'%', # 单位
        'POS':{
            'LON_LAT':[], # 坐标
            'WF':'W15117', #工作面
            'TEXT':'W15117工作面', # 描述
        }, # 位置
    },
}


def get_monitor_ids():
    return MONITOR_DEFINE.keys()

def get_monitor_by_id(monitor_id):
    if monitor_id not in MONITOR_DEFINE:
        return None
    return MONITOR_DEFINE[monitor_id]

def get_monitor_ids_by_type(typestr='CH4'):
    res = []
    for mid, v in MONITOR_DEFINE.items():
        if v['TYPE'] == typestr:
            res.append(mid)
    return res


