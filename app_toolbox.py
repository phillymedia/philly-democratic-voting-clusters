import dash_mantine_components as dmc
import pandas as pd



def get_label_str(x, label_d={}):
    return label_d.get(
        x,
        label_d.get(
            str(x),
            str(x).title().replace('_',' ') if x not in {'',None} else '[?]'
        )
    )

def get_options(data, sort_alpha=False, label_d={}):
    if type(data)==pd.Series:
        s=data.fillna('').apply(str).value_counts()
        data = [
            (f"{get_label_str(key, label_d=label_d)} ({count:,})", key) 
            for key,count in zip(s.index, s)
        ]
    else:
        data = [
            (
                (get_label_str(x, label_d=label_d), x) 
                if type(x) not in {list,tuple} 
                else x
            )
            for x in data
        ]
    return data


    
    
    return data

def get_radio_group(data=[], label='', value='', label_d={}, **kwargs):
    return dmc.RadioGroup(
        [dmc.Radio(label, value=value) for label, value in get_options(data,label_d={})],
        value=value,
        label=label,
        # size="sm",
        # mt=10,
        # className='widget-group',
        **kwargs
    )

def get_labeled_element(element, label=''):
    if not label:
        label = element.id.replace('_',' ').title() + ('?' if element.id.startswith('is_') else '')
    
    return get_card(
        children=[
            dmc.Text(label, className='mantine-InputWrapper-label'),
            element
        ],
        className='widget-group',
        shadow='xs',
        radius=0,
        withBorder=False
    )

def get_card(children=[], className='', **kwargs):
    className+=' card'
    return dmc.Card(
        children=children,
        className=className,
        **{
            **dict(
                shadow='xs', 
                withBorder=True,
                radius=10

            ),
            **kwargs
        }
    )


def get_chip_group(data=[], label='',label_d={},multiple=True,**kwargs):
    return get_labeled_element(
        dmc.ChipGroup([
            dmc.Chip(
                l,
                value=v,
                variant="filled",
                className='chip',
                type='checkbox'
            )
            for l,v in get_options(data,label_d=label_d)
            ],
            multiple=multiple,
            spacing=5,
            className='chipgroup',
            **kwargs
        ),
        label=label
    )
    



def get_range_slider(series, label='', step=10, value=None,**kwargs):
    s = pd.to_numeric(series, errors='coerce')
    minval=s.min() // step * step
    maxval=s.max() // step * step + step
    value=value if value is not None else [minval,maxval]
    slider = dmc.RangeSlider(
        min=minval,
        max=maxval,
        value=value,
        step=step,
        labelAlwaysOn=True,
        mt=35,
        className='slider',
        **kwargs
    )
    return get_labeled_element(slider, label=label)


def get_paper(children=[], className='',**kwargs):
    return dmc.Paper(
        children=children,
        **{
            **dict(
                shadow="md",
                radius='sm',
                # withBorder=True,
                className='paper '+className
            ),
            **kwargs
        }
    )