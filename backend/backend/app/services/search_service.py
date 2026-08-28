"""Database-level, paginated search helpers. Never bulk-loads records."""
from sqlalchemy import or_, and_

def paginate(query, page=1, page_size=25):
 page=max(1,int(page)); page_size=min(max(1,int(page_size)),100)
 total=query.count(); rows=query.offset((page-1)*page_size).limit(page_size).all()
 return {"items":rows,"page":page,"page_size":page_size,"total":total,"pages":(total+page_size-1)//page_size}

def apply_filters(query, model, filters):
 for field in ("name","id","blood_group","organ","hospital_id","location","availability_status","urgency","status","hla_a","hla_b","hla_c","hla_dr","hla_dq"):
  value=filters.get(field)
  if value is None or value=="": continue
  column=getattr(model,field,None)
  if column is None: continue
  query=query.filter(column.ilike(f"%{value}%") if field in ("name","location") else column==value)
 return query
