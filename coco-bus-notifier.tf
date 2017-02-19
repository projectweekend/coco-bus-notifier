variable "BUSTRACKER_TABLE_ARN" {}
variable "BUSTRACKER_TABLE_STREAM_ARN" {}
variable "BRIAN_SMS_NUMBER" {}


provider "aws" {
    profile = "default"
    region = "us-east-1"
}


data "terraform_remote_state" "coco_tfstate" {
    backend = "s3"
    config {
        bucket = "pw-terraform-state"
        key = "coco-bus-notifier/terraform.tfstate"
        profile = "default"
        region = "us-east-1"
    }
}


data "aws_iam_policy_document" "coco_lambda_assume_role_policy" {
    statement {
        actions = [ "sts:AssumeRole" ]
        principals {
            type = "Service"
            identifiers = [ "lambda.amazonaws.com", "dynamodb.amazonaws.com" ]
        }
    }
}


data "aws_iam_policy_document" "coco_lambda_iam_policy" {
    statement {
        effect = "Allow"
        actions = [
            "lambda:InvokeFunction",
        ]
        resources = [
            "${aws_lambda_function.coco_busnotifier_lambda_17772.arn}",
        ]
    }
    statement {
        effect = "Allow"
        actions = [
            "dynamodb:DescribeStream",
            "dynamodb:GetRecords",
            "dynamodb:GetShardIterator",
            "dynamodb:ListStreams"
        ]
        resources = [
            "*"
        ]
    }
    statement {
        effect = "Allow"
        actions = [
            "sns:Publish"
        ]
        resources = [
            "*"
        ]
    }
    statement {
        effect = "Allow"
        actions = [
            "logs:CreateLogGroup",
            "logs:CreateLogStream",
            "logs:PutLogEvents"
        ]
        resources = [
            "*",
        ]
    }
}


resource "aws_iam_policy" "coco_lambda_iam_policy" {
    name = "coco_busnotifier_lambda_policy"
    policy = "${data.aws_iam_policy_document.coco_lambda_iam_policy.json}"
}


resource "aws_iam_role" "coco_busnotifier_lambda_iam_role" {
    name = "coco_busnotifier_lambda"
    assume_role_policy = "${data.aws_iam_policy_document.coco_lambda_assume_role_policy.json}"
}


resource "aws_iam_role_policy_attachment" "coco_lambda_iam_policy_attach" {
    role = "${aws_iam_role.coco_busnotifier_lambda_iam_role.name}"
    policy_arn = "${aws_iam_policy.coco_lambda_iam_policy.arn}"
}


resource "aws_lambda_function" "coco_busnotifier_lambda_17772" {
    filename = "lambda.zip"
    function_name = "coco_busnotifier_lambda_17772"
    role = "${aws_iam_role.coco_busnotifier_lambda_iam_role.arn}"
    handler = "main.lambda_handler"
    runtime = "python2.7"
    timeout = 10
    source_code_hash = "${base64sha256(file("lambda.zip"))}"
    environment {
        variables = {
            TIME_TO_STOP = "240"
            SMS_NUMBER = "${var.BRIAN_SMS_NUMBER}"
        }
    }
}


resource "aws_lambda_event_source_mapping" "event_source_mapping" {
    batch_size = 100
    event_source_arn = "${var.BUSTRACKER_TABLE_STREAM_ARN}"
    enabled = true
    function_name = "coco_busnotifier_lambda_17772"
    starting_position = "LATEST"
}
