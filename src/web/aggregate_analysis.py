import os, sys, time
sys.path.append(os.path.join(os.path.dirname(__file__) ,'.'))
from decision.gas_analysis import GasAnalysisEventType
from launch import time_delta

def aggregate_event(gas_analysis_obj):
    # 渲染gas_analysis_obj event
    res = {}
    if not gas_analysis_obj.update:
        res['update'] = False
        return res

    res['update'] = True
    gas_analysis_event = gas_analysis_obj.result_event
    event_items = []

    # over_limit
    for status_obj in gas_analysis_event.over_limit_list:
        time_str = str(status_obj.timestamp)
        location_name = str(status_obj.monitor['POS']['TEXT'])
        mid = str(status_obj.monitor_id)
        val = str(status_obj.activate_facts[0]['val'])
        content = "[瓦斯 超限] %s处瓦斯监测点(编号为%s）瓦斯超限，当前浓度为%s" \
                    % (location_name, mid, val)
        wrapper = "<div class='alert alert-danger' role='alert'> %s </div>" % content
        # print(wrapper)
        event_items.append(wrapper)
    # pred_over_limit
    for status_obj in  gas_analysis_event.pred_over_limit_list:
        time_str = str(status_obj.timestamp)
        location_name = str(status_obj.monitor['POS']['TEXT'])
        mid = str(status_obj.monitor_id)
        val = str(status_obj.activate_facts[0]['val'])
        content = "[瓦斯 预警] %s处瓦斯监测点(编号为%s）瓦斯预计在%s分钟后超限，当前浓度为%s" \
                    % (location_name, mid,status_obj.pred_over_limit_index * time_delta ,val)
        wrapper = "<div class='alert alert-warning' role='alert'> %s </div>" % content
        # print(wrapper)
        event_items.append(wrapper)

    if len(event_items) == 0:
        res['content'] = "<div class='alert alert-success' role='alert'> 当前无异常情况。</div>"
    else:
        res['content'] = ' '.join(event_items)

    if gas_analysis_event.event_type in [GasAnalysisEventType.OVER_LEVEL_1, GasAnalysisEventType.OVER_LEVEL_2]:
        color_type = 'danger'
    elif gas_analysis_event.event_type in [GasAnalysisEventType.PRED_LEVEL_1, GasAnalysisEventType.PRED_LEVEL_2]:
        color_type = 'warning'
    else:
        color_type = 'success'


    # summery 相关内容
    res['summery_title'] = "<h3><span class='label label-%s'>%s</span></h3>" % (color_type, gas_analysis_event.get_title())
    res['summery_content'] = "<div class='alert alert-%s' role='alert'> <h5> %s</h5> </div>" % (color_type,gas_analysis_event.get_detail())
    return res


