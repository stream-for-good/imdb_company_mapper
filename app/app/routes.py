from app.models import Company, Content

import json
from flask import request, make_response, render_template, abort, Response
from app.main import app
from app.main import db
from app.set_encoder import SetEncoder
import datetime
import logging
import os
import sqlalchemy


def get_api_root():
    return os.getenv("API_ROOT", "dummy://")


@app.route("/", methods=["GET"])
def home():
    return json.dumps({"links": [{"rel": "companies", "href": get_api_root() + "/companies"},
                                 {"rel": "contents", "href": get_api_root() + "/contents"}]}, cls=SetEncoder), 200, {
               'Content-Type': 'application/json'}


@app.route("/companies", methods=["GET"])
def get_companies():
    companies = db.session.query(Company).all()
    return json.dumps(
        [{"company_id": company.id,
          "links": get_company_links(company.id)
          } for company in companies]

        , cls=SetEncoder), 200, {
               'Content-Type': 'application/json'}


@app.route("/contents", methods=["GET"])
def get_contents():
    contents = db.session.query(Content).all()
    return json.dumps(
        [{"content_id": content.id,
          "links": get_content_links(content.id)
          } for content in contents]

        , cls=SetEncoder), 200, {
               'Content-Type': 'application/json'}


@app.route("/content/<tt_code>", methods=["POST"])
def post_content(tt_code):
    content = db.session.query(Content).filter(Content.id == tt_code).first()
    if content is not None:
        return abort(409)
    payload = request.get_json()
    company_names = payload["company_names"]

    content = Content()
    content.id = tt_code

    for company_name in company_names:
        company = db.session.query(Company).filter(Company.name == company_name).first()
        if company is None:
            return abort(404, f"Company {company_name} is not known")
        content.companies.append(company)

    db.session.add(content)
    db.session.commit()

    return make_response("CREATED", 201)


def get_company_links(id):
    return [{"rel": "company", "href": f"{get_api_root()}/company/{id}"}]


def get_content_links(id):
    return [{"rel": "content", "href": f"{get_api_root()}/content/{id}"}]


@app.route("/content/<tt_code>", methods=["GET"])
def get_content(tt_code):
    content = db.session.query(Content).filter(Content.id == tt_code).first()
    if content is None:
        return abort(404)
    res = {"content_id": tt_code,
           "company_ids": [{"imdb_id": company.id} for company in content.companies],
           "links": [{"rel": "companies", "href": get_api_root() + f"/content/{tt_code}/companies"}]}
    return json.dumps(res, cls=SetEncoder), 200, {'Content-Type': 'application/json'}


@app.route("/content/<tt_code>/companies", methods=["GET"])
def get_companies_for_content(tt_code):
    content = db.session.query(Content).filter(Content.id == tt_code).first()
    if content is None:
        return abort(404)
    res = [
        {"company_id": company.id, "link": [get_company_links(company.id)]} for company in content.companies
    ]
    return json.dumps(res, cls=SetEncoder), 200, {'Content-Type': 'application/json'}


@app.route("/company/<cc_code>", methods=["POST"])
def post_company(cc_code):
    company = db.session.query(Company).filter(Company.id == cc_code).first()
    if company is not None:
        return abort(409)
    payload = request.get_json()
    name = payload["name"]
    link = payload["link"]

    create_company(cc_code, link, name)

    return make_response("CREATED", 201)


def create_company(cc_code, link="", name=""):
    company = Company()
    company.id = cc_code
    company.name = name
    company.link = link
    db.session.add(company)
    db.session.commit()


@app.route("/company/<cc_code>", methods=["GET"])
def get_company(cc_code):
    company = db.session.query(Company).filter(Company.id == cc_code).first()
    if company is None:
        return abort(409)

    res = {"company_id": company.id, "name": company.name, "link": company.link,
           "contents": [{"imdb_id": content.id, "links": get_content_links(content.id)} for content in
                        company.contents]}

    return json.dumps(res, cls=SetEncoder), 200, {'Content-Type': 'application/json'}
