# -*- coding: utf-8 -*-

from google.appengine.api import search
from lib.models import Message

from logging import getLogger
logger = getLogger(__name__)


class SearchApiHandler(object):

    INDEX_NAME = 'message_index'
    MSG_PER_PAGE_NUM = 100

    def __init__(self):
        self.index = search.Index(name=self.INDEX_NAME)

    def put_all_documents(self):
        logger.debug('enter')
        for msg in Message.query():
            self.put_one_document(msg)
        logger.debug('exit')

    def put_one_document(self, msg):
        doc_id = '{channel_id}_{user}_{ts}'.format(channel_id=msg.channel_id, user=msg.user, ts=int(msg.ts))

        doc = search.Document(
            doc_id=doc_id,
            fields=[search.TextField(name='text', value=msg.text),
                    search.AtomField(name='user_name', value=msg.get_user_name()),
                    search.AtomField(name='channel_id', value=msg.channel_id),
                    search.AtomField(name='msg_key', value=str(msg.key.id())),
                    search.DateField(name='ts', value=msg.get_datetime()),
                    ]
        )
        # Index the document.
        try:
            self.index.put(doc)
        except search.PutError, e:
            result = e.results[0]
            if result.code == search.OperationResult.TRANSIENT_ERROR:
                # possibly retry indexing result.object_id
                return self.put_one_document(msg)
        except search.Error, e:
            # possibly log the failure
            logger.error('%s' % e.msg)
            raise e

    def search_query(self, query_string, page=0):

        # Create sort options to sort on price and brand.
        sort_ts = search.SortExpression(
            expression='ts',
            direction=search.SortExpression.DESCENDING,
            default_value=0)
        sort_options = search.SortOptions(expressions=[sort_ts])

        # Create query options using the sort options and expressions created
        # above.
        query_options = search.QueryOptions(
            limit=self.MSG_PER_PAGE_NUM,
            offset=page * self.MSG_PER_PAGE_NUM,
            returned_fields=['msg_key'],
            sort_options=sort_options)

        # Build the Query and run the search
        try:
            query = search.Query(query_string=query_string, options=query_options)
        except search.QueryError:
            return []
        results = self.index.search(query)

        return results


if __name__ == '__main__':
    pass
