import decimal
import datetime

import dateutil.parser

from charon import CodecRegistry



#: Module Variable for Registry with Dumpers and Loaders for standard Python Types
STANDARD_REGISTRY = CodecRegistry()


@STANDARD_REGISTRY.dumper(decimal.Decimal, version = 1)
def _dump_decimal_v1(obj):
	return str(obj)


@STANDARD_REGISTRY.loader(decimal.Decimal, version = 1)
def _load_decimal_v1(data):
	return decimal.Decimal(data)


@STANDARD_REGISTRY.dumper(set, version = 1)
def _dump_set_v1(obj):
	return list(obj)


@STANDARD_REGISTRY.loader(set, version = 1)
def _load_set_v1(data):
	return set(data)


@STANDARD_REGISTRY.dumper(frozenset, version = 1)
def _dump_frozenset_v1(obj):
	return list(obj)


@STANDARD_REGISTRY.loader(frozenset, version = 1)
def _load_frozenset_v1(data):
	return frozenset(data)


@STANDARD_REGISTRY.dumper(datetime.datetime, version = 1)
def _dump_datetime_v1(obj):
	return obj.isoformat()


@STANDARD_REGISTRY.loader(datetime.datetime, version = 1)
def _load_datetime_v1(data):
	return dateutil.parser.parse(data)


@STANDARD_REGISTRY.dumper(datetime.datetime, version = 2)
def _dump_datetime_v2(obj):
	return (int(obj.timestamp()), obj.microsecond * 1000, obj.utcoffset(),)


@STANDARD_REGISTRY.loader(datetime.datetime, version = 2)
def _load_datetime_v2(data):
	timestamp, nanoseconds, utcoffset = data
	if utcoffset is None:
		obj = datetime.datetime.fromtimestamp(timestamp)
		obj.replace(microsecond = nanoseconds // 1000)
	else:
		obj = datetime.datetime.fromtimestamp(timestamp, tz = datetime.timezone(utcoffset))
		obj.replace(microsecond = nanoseconds // 1000)
	return obj


@STANDARD_REGISTRY.dumper(datetime.date, version = 1)
def _dump_date_v1(obj):
	return obj.isoformat()


@STANDARD_REGISTRY.loader(datetime.date, version = 1)
def _load_date_v1(data):
	return dateutil.parser.parse(data).date()


@STANDARD_REGISTRY.dumper(datetime.date, version = 2)
def _dump_date_v2(obj):
	return (obj.year, obj.month, obj.day)


@STANDARD_REGISTRY.loader(datetime.date, version = 2)
def _load_date_v2(data):
	return datetime.date(*data)


@STANDARD_REGISTRY.dumper(datetime.time, version = 1)
def _dump_time_v1(obj):
	return obj.isoformat()


@STANDARD_REGISTRY.loader(datetime.time, version = 1)
def _load_time_v1(data):
	return dateutil.parser.parse(data).time()


@STANDARD_REGISTRY.dumper(datetime.time, version = 2)
def _dump_time_v2(obj):
	return (obj.hour, obj.minute, obj.second, obj.microsecond * 1000)


@STANDARD_REGISTRY.loader(datetime.time, version = 2)
def _load_time_v2(data):
	hour, minute, second, nanosecond = data
	return datetime.time(hour, minute, second, nanosecond // 1000)


@STANDARD_REGISTRY.dumper(datetime.timedelta, version = 1)
def _dump_timedelta_v1(obj):
	return {'days': obj.days, 'seconds': obj.seconds, 'microseconds': obj.microseconds}


@STANDARD_REGISTRY.loader(datetime.timedelta, version = 1)
def _load_timedelta_v1(data):
	return datetime.timedelta(days = data['days'], seconds = data['seconds'], microseconds = data['microseconds'])


@STANDARD_REGISTRY.dumper(datetime.timedelta, version = 2)
def _dump_timedelta_v2(obj):
	return (obj.days, obj.seconds, obj.microseconds,)


@STANDARD_REGISTRY.loader(datetime.timedelta, version = 2)
def _load_timedelta_v2(data):
	days, seconds, microseconds = data
	return datetime.timedelta(days = days, seconds = seconds, microseconds = microseconds)
