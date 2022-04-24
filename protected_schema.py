protection_data = {
            "required_status_checks" : None,
            # {
            #     "strict " : True,
            #     "contexts" : [],
            #     "checks" : [
            #         {
            #             "context" : ""
            #         }
            #     ]
            # },
            "enforce_admins" : True,
            "required_pull_request_reviews" : {
                "dismissal_restrictions" : {
                    "users" : [],
                    "teams" : []
                },
                "dismiss_stale_reviews" : True,
                "require_code_owner_reviews" : True,
                "required_approving_review_count" : 2,
                "bypass_pull_request_allowances" : {
                    "users" : [],
                    "teams" : []
                }
            },
            "restrictions" : {
                "users" : ["nwhewell"],
                "teams" : [],
                "apps" : [],
            },
            "required_linear_history" : True,
            "allow_force_pushes" : False,
            "allow_deletions" : False,
            "block_creations" : True,
            "required_conversation_resolution" : True
            
        }
