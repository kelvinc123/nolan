

class Matcher:

    def __init__(self, mongo):
        self.mongo = mongo
    
    def _get_zipcode_distance(self, zip_code):
        distances = self.mongo.db.zip_25miles_distances.find({"zip1": int(zip_code)}).sort("miles_to_zcta5", 1)
        return [dist for dist in distances]
    
    def _get_presences(self, distances):
        '''
        Method to get all line sitters that are located in one of the distances value ()

        Returns a list of 
        '''
        acceptable_zip_codes = [str(dist["zip2"]) for dist in distances]
        presences = self.mongo.db.presences.find({"zip_code": {"$in": acceptable_zip_codes}})

        result = []
        for p in presences:
            # add distance to dict
            p["distance"] = float(
                [dist["miles_to_zcta5"] for dist in distances if str(dist["zip2"]) == str(p["zip_code"])][0]
            )
            result.append(p)

        # sort by distance
        result = sorted(result, key=lambda x: x["distance"], reverse=False)
        return result
    
    def match_line_sitter(self, zip_code):
        distances = self._get_zipcode_distance(zip_code=zip_code)
        line_sitters = self._get_presences(distances=distances)
        
        return line_sitters
