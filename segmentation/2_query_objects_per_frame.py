import pandas as pd
import json


# Helper functions for bounding boxes
def is_within(object_box, query_box):
    """Returns True if object_box is completely within query_box"""
    x1, y1, x2, y2 = object_box
    qx1, qy1, qx2, qy2 = query_box
    return qx1 <= x1 and qy1 <= y1 and qx2 >= x2 and qy2 >= y2

def is_partially_within(object_box, query_box):
    """Returns True if object_box and query_box overlap at all"""
    x1, y1, x2, y2 = object_box
    qx1, qy1, qx2, qy2 = query_box
    return not (x2 < qx1 or x1 > qx2 or y2 < qy1 or y1 > qy2)




def parse_queries(query_file):
    """Parse CSV file with columns 'object' and optional 'bounding_box'"""
    df = pd.read_csv(query_file)
    df['name'] = df['object'] 
    # optional bounding box
    df.loc[pd.notna(df['bounding_box']), 'name'] = df['name'] + ', bbox=' + df['bounding_box'].astype(str)
    queries = df.to_dict(orient='records')
    return queries


def count_objects(found_objects, query, bbox_mode='full'):
    """
    found_objects: dict of objects for one frame
    query: dict with keys 'object' and optional 'bounding_box'
    bbox_mode: 'full' or 'partial'
    """
    obj_type = query['object']
    query_bbox = None
    if 'bounding_box' in query and pd.notna(query['bounding_box']):
        query_bbox = tuple(map(int, query['bounding_box'].strip('[]').split(',')))

    count = 0
    if obj_type in found_objects:
        for obj in found_objects[obj_type]:
            if query_bbox is None:
                count += 1
            else:
                if bbox_mode == 'full' and is_within(obj['bbox'], query_bbox):
                    count += 1
                elif bbox_mode == 'partial' and is_partially_within(obj['bbox'], query_bbox):
                    count += 1
    return count


def query_frames(found_objects_jsonl, queries, bbox_mode='full'):
    """Process the JSONL file with objects per frame and count occurrences of each query"""
    records = []

    with open(found_objects_jsonl, 'r') as f:
        for line in f:
            record = json.loads(line) 
            frame_name = list(record.keys())[0]
            found_objects = record[frame_name]

            frame_record = {'frame': frame_name}
            for query in queries:
                count = count_objects(found_objects, query, bbox_mode)
                frame_record[query['name']] = count

            records.append(frame_record)

    df = pd.DataFrame(records)
    return df


if __name__ == "__main__":
    query_file = 'example_queries.csv'
    found_objects_jsonl = 'objects_per_frame_example.jsonl'
    output_file = 'queries_df.csv'

    queries = parse_queries(query_file)
    queries_df = query_frames(found_objects_jsonl, queries, bbox_mode='partial')

    queries_df.to_csv(output_file, index=False)