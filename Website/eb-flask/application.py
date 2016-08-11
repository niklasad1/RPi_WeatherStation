from bokeh.plotting import figure
from bokeh.embed import components
from bokeh.models import TapTool, HoverTool, ColumnDataSource, DatetimeTickFormatter, DatetimeAxis, NumeralTickFormatter, Range1d
from flask import Flask, render_template, make_response
from flask_pymongo import PyMongo
from flask.ext import excel

application = Flask(__name__)
application.config['MONGO_DBNAME'] = 'weatherstation'
application.config['MONGO_URI'] = 'mongodb://pi:raspberry@ds029665.mlab.com:29665/weatherstation'
mongo = PyMongo(application, config_prefix='MONGO')


@application.route('/')
@application.route('/temperature')
def temp():
    data = { 'temp': [],
             'temp_min': [],
             'temp_max': [],
             'date': [],
             'date_formatted': []
       }

    for item in mongo.db.ws.find():
        data['temp'].append(float(item['TemperatureAverage']))
        data['date'].append(item['date'])
        data['date_formatted'].append(item['date'].strftime('%a %d %b'))
        data['temp_min'].append(item['TemperatureMin'])
        data['temp_max'].append(item['TemperatureMax'])

    source = ColumnDataSource(data=data)

    plot = figure(
        x_axis_type='datetime',
        plot_height=500, plot_width=700,
        title="Temperature",
        tools="hover, wheel_zoom, pan, tap",
        y_range=Range1d(start=-10.0, end=40.0)
    )

    plot.line('date', 'temp', line_width=2, color='navy', source=source)
    plot.circle('date', 'temp', size=10, color='navy', source=source)


    plot.xaxis.axis_label = "Date"
    plot.xaxis.axis_label_text_font_size = "12pt"
    plot.xaxis.axis_line_width = 3
    plot.xaxis.formatter = DatetimeTickFormatter(
                            formats=dict(
                                hours=["%Y-%m-%d"],
                                days=["%Y-%m-%d"],
                                months=["%Y-%m-%d"],
                                years=["%Y-%m-%d"],
                            )
    )
    plot.xaxis.axis_line_color = "red"

    # change just some things about the y-axes
    plot.yaxis.axis_label = 'Temperature ' + '('  u'\xb0' + 'C)'
    plot.yaxis.axis_label_text_font_size = "12pt"
    plot.yaxis.major_label_text_color = "orange"
    plot.yaxis.major_label_orientation = "horizontal"

    # change things on all axes
    plot.axis.minor_tick_in = -3
    plot.axis.minor_tick_out = 6

    hover = plot.select(type=HoverTool)
    hover.tooltips  = """
        <div>
        <span style="font-size: 15px; font-weight: bold;">@date_formatted</span>
        </div>
        <table border="0" cellpadding="10">
        <tr>
            <th><span style="font-family:'Consolas'- 'Lucida Console', monospace; font-size: 12px;">average: </span></th>
            <td><span style="font-family:'Consolas', 'Lucida Console', monospace; font-size: 12px;">@temp</span></td>
        </tr>
        <tr>
            <th><span style="font-family:'Consolas', 'Lucida Console', monospace; font-size: 12px;">min: </span></th>
            <td><span style="font-family:'Consolas', 'Lucida Console', monospace; font-size: 12px;">@temp_min</span></td>
        </tr>
        <tr>
            <th><span style="font-family:'Consolas', 'Lucida Console', monospace; font-size: 12px;">max: </span></th>
            <td><span style="font-family:'Consolas', 'Lucida Console', monospace; font-size: 12px;">@temp_max</span></td>
        </tr>
    </table>
    """
    script, div = components(plot)
    return(render_template('temperature.html', div=div, script=script))


@application.route('/humidity', methods=('GET', ))
def humidity():
    data = { 'hum': [],
             'hum_min': [],
             'hum_max': [],
             'hum_dec': [],
             'hum_min_dec': [],
             'hum_max_dec': [],
             'date': [],
             'date_formatted': []
       }

    for item in mongo.db.ws.find():
        data['date'].append(item['date'])
        data['date_formatted'].append(item['date'].strftime('%a %d %b'))
        data['hum'].append(abs(float(item['HumidityAverage'])))
        data['hum_min'].append(abs(item['HumidityMin']))
        data['hum_max'].append(abs(item['HumidityMax']))
        data['hum_dec'].append(abs(float(item['HumidityAverage']/100)))


    source = ColumnDataSource(data=data)

    plot = figure(
        x_axis_type='datetime',
        plot_height=500, plot_width=700,
        title="Humidity",
        tools="hover, wheel_zoom, pan, tap",
        y_range=Range1d(start=0.0, end=1.0)
    )

    plot.line('date', 'hum_dec', line_width=2, color='navy', source=source)
    plot.circle('date', 'hum_dec', size=10, color='navy', source=source)


    plot.xaxis.axis_label = "Date"
    plot.xaxis.axis_label_text_font_size = "12pt"
    plot.xaxis.axis_line_width = 3
    plot.xaxis.formatter = DatetimeTickFormatter(
                            formats=dict(
                                hours=["%Y-%m-%d"],
                                days=["%Y-%m-%d"],
                                months=["%Y-%m-%d"],
                                years=["%Y-%m-%d"],
                            )
    )
    plot.xaxis.axis_line_color = "red"

    # change just some things about the y-axes
    plot.yaxis.axis_label = "Humidity(%)"
    plot.yaxis.axis_label_text_font_size = "12pt"
    plot.yaxis.major_label_text_color = "orange"
    plot.yaxis.major_label_orientation = "horizontal"
    plot.yaxis.formatter = NumeralTickFormatter(format="0%")

    # change things on all axes
    plot.axis.minor_tick_in = -3
    plot.axis.minor_tick_out = 6

    hover = plot.select(type=HoverTool)
    hover.tooltips  = """
        <div>
        <span style="font-size: 15px; font-weight: bold;">@date_formatted</span>
        </div>
        <table border="0" cellpadding="10">
        <tr>
            <th><span style="font-family:'Consolas', 'Lucida Console', monospace; font-size: 12px;">average: </span></th>
            <td><span style="font-family:'Consolas', 'Lucida Console', monospace; font-size: 12px;">@hum%</span></td>
        </tr>
        <tr>
            <th><span style="font-family:'Consolas', 'Lucida Console', monospace; font-size: 12px;">min: </span></th>
            <td><span style="font-family:'Consolas', 'Lucida Console', monospace; font-size: 12px;">@hum_min%</span></td>
        </tr>
        <tr>
            <th><span style="font-family:'Consolas', 'Lucida Console', monospace; font-size: 12px;">max: </span></th>
            <td><span style="font-family:'Consolas', 'Lucida Console', monospace; font-size: 12px;">@hum_max%</span></td>
        </tr>
    </table>
    """
    script, div = components(plot)
    return(render_template('humidity.html',div=div, script=script))

@application.route('/pressure', methods=('GET',))
def pressure():
    data = { 'pres': [],
             'pres_min': [],
             'pres_max': [],
             'date': [],
             'date_formatted': []
       }

    for item in mongo.db.ws.find():
        data['pres'].append(float(item['PressureAverage']))
        data['date'].append(item['date'])
        data['date_formatted'].append(item['date'].strftime('%a %d %b'))
        data['pres_min'].append(item['PressureMin'])
        data['pres_max'].append(item['PressureMax'])

    source = ColumnDataSource(data=data)

    plot = figure(
        x_axis_type='datetime',
        plot_height=500, plot_width=700,
        title="Pressure",
        tools="hover, wheel_zoom, pan, tap",
        y_range=Range1d(start=0.0, end=2000.0)
    )

    plot.line('date', 'pres', line_width=2, color='navy', source=source)
    plot.circle('date', 'pres', size=10, color='navy', source=source)


    plot.xaxis.axis_label = "Date"
    plot.xaxis.axis_label_text_font_size = "12pt"
    plot.xaxis.axis_line_width = 3
    plot.xaxis.formatter = DatetimeTickFormatter(
                            formats=dict(
                                hours=["%Y-%m-%d"],
                                days=["%Y-%m-%d"],
                                months=["%Y-%m-%d"],
                                years=["%Y-%m-%d"],
                            )
    )
    plot.xaxis.axis_line_color = "red"

    # change just some things about the y-axes
    plot.yaxis.axis_label = "Pressure (millibars)"
    plot.yaxis.axis_label_text_font_size = "12pt"
    plot.yaxis.major_label_text_color = "orange"
    plot.yaxis.major_label_orientation = "horizontal"

    # change things on all axes
    plot.axis.minor_tick_in = -3
    plot.axis.minor_tick_out = 6

    hover = plot.select(type=HoverTool)
    hover.tooltips  = """
        <div>
        <span style="font-size: 15px; font-weight: bold;">@date_formatted</span>
        </div>
        <table border="0" cellpadding="10">
        <tr>
            <th><span style="font-family:'Consolas'- 'Lucida Console', monospace; font-size: 12px;">average: </span></th>
            <td><span style="font-family:'Consolas', 'Lucida Console', monospace; font-size: 12px;">@pres</span></td>
        </tr>
        <tr>
            <th><span style="font-family:'Consolas', 'Lucida Console', monospace; font-size: 12px;">min: </span></th>
            <td><span style="font-family:'Consolas', 'Lucida Console', monospace; font-size: 12px;">@pres_min</span></td>
        </tr>
        <tr>
            <th><span style="font-family:'Consolas', 'Lucida Console', monospace; font-size: 12px;">max: </span></th>
            <td><span style="font-family:'Consolas', 'Lucida Console', monospace; font-size: 12px;">@pres_max</span></td>
        </tr>
    </table>
    """
    script, div = components(plot)
    return(render_template('pressure.html', div=div, script=script))


@application.route('/export', methods=('GET',))
def export():
    csv_test =  [
                    ['Date','HumidityAverage', 'HumidityMax', 'HumidityMin',
                     'PressureAverage', 'PressureMax', 'PressureMin',
                     'TemperatureAverage', 'TemperatureMax', 'TemperatureMin']
                ]

    for item in mongo.db.ws.find():
        csv_test.append([
            str(item['date'].strftime('%Y-%m-%d')),
            abs(float(item['HumidityAverage'])/100),
            abs(float(item['HumidityMax'])/100),
            abs(float(item['HumidityMin'])/100),
            item['PressureAverage'],
            item['PressureMax'],
            item['PressureMin'],
            item['TemperatureAverage'],
            item['TemperatureMax'],
            item['TemperatureMin']
        ])

    response = excel.make_response_from_array(csv_test, 'csv')
    response.headers["Content-Disposition"] = "attachment; filename=measurements.csv"
    response.headers["Content-type"] = "text/csv"
    return response
if __name__ == '__main__':
    application.run()
