# -*- coding: utf-8 -*-
# Copyright 2017-TODAY LasLabs Inc.
# License MIT (https://opensource.org/licenses/MIT).

import mock
import unittest

from .. import BaseApi
from .. import BaseModel
from ..domain import Domain
from ..request_paginator import RequestPaginator


PAGINATOR = 'helpscout.base_api.RequestPaginator'


class TestApi(BaseApi):
    __object__ = BaseModel


class TestBaseApi(unittest.TestCase):

    ENDPOINT = '/endpoint'
    DATA = {'test': 1234}
    REQUEST_TYPE = RequestPaginator.POST

    def new_api(self, endpoint=ENDPOINT, data=DATA, request_type=REQUEST_TYPE,
                singleton=False, session=None, out_type=None):
        return TestApi(
            endpoint, data, request_type, singleton, session, out_type,
        )

    def test_new(self):
        """It should return a new TestApi instance."""
        self.assertIsInstance(self.new_api(), TestApi)

    def test_new_paginator(self):
        """It should return a new API object with a paginator."""
        self.assertIsInstance(self.new_api().paginator, RequestPaginator)

    def test_new_paginator_create(self):
        """It should create the paginator with the proper args."""
        session = 'session'
        with mock.patch.object(RequestPaginator, '__init__') as init:
            init.return_value = None
            self.new_api(session=session)
            init.assert_called_once_with(
                endpoint='https://api.helpscout.net/v1%s' % self.ENDPOINT,
                data=self.DATA,
                output_type=TestApi.__object__.from_api,
                request_type=self.REQUEST_TYPE,
                session=session,
            )

    @mock.patch(PAGINATOR)
    def test_new_paginator_singleton(self, paginator):
        """It should return the record if singleton and found."""
        paginator().call.return_value = [{'id': 9876}]
        res = self.new_api(singleton=True)
        self.assertIsInstance(res, BaseModel)
        self.assertEqual(res.id, 9876)

    @mock.patch(PAGINATOR)
    def test_new_paginator_singleton_not_found(self, paginator):
        """It should return None if singleton and not found."""
        paginator().call.return_value = []
        res = self.new_api(singleton=True)
        self.assertIs(res, None)

    @mock.patch(PAGINATOR)
    def test_new_paginator_singleton_none(self, paginator):
        """It should return None if singleton and return value is None."""
        paginator().call.return_value = None
        res = self.new_api(singleton=True)
        self.assertIs(res, None)

    @mock.patch(PAGINATOR)
    def test_base_api_iterates_paginator(self, paginator):
        """It should pass iteration to the paginator."""
        expect = [BaseModel(id=1), BaseModel(id=2)]
        paginator().call.return_value = expect
        for idx, value in enumerate(self.new_api()):
            self.assertEqual(value, expect[idx])

    @mock.patch(PAGINATOR)
    def test_new_paginator_singleton_out_type(self, paginator):
        """It should return an object of the correct type if defined."""
        paginator().call.return_value = [{'id': 9876}]
        res = self.new_api(singleton=True, out_type=mock.MagicMock())
        self.assertIsInstance(res, mock.MagicMock)

    def test_get_search_domain_domain(self):
        """It should return the input if it is a `Domain` obj."""
        expect = Domain()
        self.assertEqual(BaseApi.get_search_domain(expect), expect)

    def test_get_search_domain_tuple(self):
        """It should return the input if it is a `Domain` obj."""
        expect = [('state', True)]
        with mock.patch.object(Domain, 'from_tuple') as from_tuple:
            res = BaseApi.get_search_domain(expect)
            from_tuple.assert_called_once_with(expect)
            self.assertEqual(res, from_tuple())

    def test_new_object(self):
        """It should return the proper object."""
        expect = 123
        res = BaseApi.new_object({'id': expect})
        self.assertIsInstance(res, BaseModel)
        self.assertEqual(res.id, expect)
