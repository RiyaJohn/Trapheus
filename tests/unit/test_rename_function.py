import os
import unittest
from mock import patch, Mock
import sys
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__),'../../src/rename')))
import mock_import
import rename_function

class TestResourceProvider(unittest.TestCase):
    def test_rename_success(self):
        os.environ["Region"] = "us-west-2"
        factory_patch = patch('rename_function.boto3.client')
        mock_factory_boto_client = factory_patch.start()
        mock_response = Mock(name='response')
        mock_factory_boto_client.return_value = mock_response
        mock_response.return_value = {"taskname": "Rename", "identifier": "database-1-temp"}
        event = create_event()
        data = rename_function.lambda_rename_dbinstance(event, {})
        self.assertEqual(data.get("taskname"), "Rename")
        self.assertEqual(data.get("identifier"), "database-1-temp")

    def test_rename_revert_success(self):
        os.environ["Region"] = "us-west-2"
        factory_patch = patch('rename_function.boto3.client')
        mock_factory_boto_client = factory_patch.start()
        mock_response = Mock(name='response')
        mock_factory_boto_client.return_value = mock_response
        mock_response.return_value = {"taskname": "Rename", "identifier": "database-1"}
        event = {"Error": "InstanceRestoreException", "Cause": "Identifier:database-1 \n ThrottlingError: Rate exceeded"}
        data = rename_function.lambda_rename_dbinstance(event, {})
        self.assertEqual(data.get("taskname"), "Rename")
        self.assertEqual(data.get("identifier"), "database-1")

    def test_rename_rateexceeded_failure(self):
        os.environ["Region"] = "us-west-2"
        factory_patch = patch('rename_function.boto3.client')
        mock_factory_boto_client = factory_patch.start()
        mock_response = Mock(name='response')
        mock_factory_boto_client.return_value = mock_response
        mock_factory_boto_client.side_effect = Exception("DBInstanceIdentifier:database-1-temp \nthrottling error: Rate exceeded")
        mock_response.side_effect = Exception("DBInstanceIdentifier:database-1-temp \nthrottling error: Rate exceeded")
        event = create_event()
        try:
            rename_function.lambda_rename_dbinstance(event, {})
        except Exception as ex:
            self.assertEqual(str(ex), "DBInstanceIdentifier:database-1-temp \nthrottling error: Rate exceeded")

    def test_rename_failure(self):
        os.environ["Region"] = "us-west-2"
        factory_patch = patch('rename_function.boto3.client')
        mock_factory_boto_client = factory_patch.start()
        mock_response = Mock(name='response')
        mock_factory_boto_client.return_value = mock_response
        mock_factory_boto_client.side_effect = Exception("DBInstanceIdentifier:database-1-temp \nDBInstanceNotFound")
        mock_response.side_effect = Exception("DBInstanceIdentifier:database-1-temp \nDBInstanceNotFound")
        event = create_event()
        try:
            rename_function.lambda_rename_dbinstance(event, {})
        except Exception as ex:
            self.assertEqual(str(ex), "DBInstanceIdentifier:database-1-temp \nDBInstanceNotFound")

def create_event():
    event = { "identifier": "database-1"}
    return event