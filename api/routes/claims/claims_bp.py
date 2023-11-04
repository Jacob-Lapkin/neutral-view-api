# pylint: disable=broad-exception-caught
from flask import Blueprint, current_app, jsonify, request
from flask_jwt_extended import get_jwt_identity, jwt_required

from ...utils.fact_checker.checker import ClaimChecker

# set blueprint for claims
claims_bp = Blueprint("claims_bp", __name__)


@claims_bp.route('/claims', methods=["GET", "POST"])
@jwt_required()
def claims():
    try:
        # get db instance
        db = current_app.db

        # get current user
        user = get_jwt_identity()

        # fetch data
        data = request.get_json()
        claim = data.get('claim', None)

        if not claim:
            return jsonify({"status":"error", "message":"claim data is required"}), 400
        
        # set claim and unpack analyze claim
        claim_analysis = ClaimChecker()
        claim_analysis.set_claim(claim=claim)
        analysis_response, analysis_usage = claim_analysis.analyze_claim()

        # unack response
        fact_score = analysis_response.fact_score
        explanation = analysis_response.explanation
        icon = analysis_response.icons_list
        source_url = analysis_response.source_url

        # unpack usage
        total_cost = analysis_usage.total_cost
        total_tokens = analysis_usage.total_tokens

        claim_usage = {
                "totalCost": total_cost, 
                "totalTokens" : total_tokens
        }

        claim_data = {
                "factScore" : fact_score, 
                "explanation" : explanation, 
                "icon" : icon, 
                "sourceUrl" : source_url
        }
        # insert into usage and claims
        new_claim = db.claims.insert_one({"email":user, "claimData": claim_data, "usage":claim_usage, "claim":claim})

        return jsonify({"status":"success", "claimResponse":{"claim":claim,"claimUsage":claim_usage, "claimData":claim_data, "claimId":str(new_claim.inserted_id)}}), 200

    except Exception as error:
        return jsonify({"status":"error", "message":f"server error was encountered {error}"}), 500
