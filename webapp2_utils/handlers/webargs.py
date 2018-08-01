from __future__ import absolute_import

import dateutil.tz
import webargs.fields


class UtcDateTime(webargs.fields.DateTime):
    """
    UTC datetime field for webargs validation.
    """

    def _deserialize(self, value, attr, data):

        result = super(UtcDateTime, self)._deserialize(value, attr, data)

        if result.tzinfo:
            result = result.astimezone(dateutil.tz.tzutc())
            result = result.replace(tzinfo=None)

        return result
