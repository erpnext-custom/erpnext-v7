select e.name as name, e.equipment_type as ty, e.equipment_number as no, e.branch br, vl.place, 
	(select (sum(pol.qty*pol.rate)/sum(pol.qty)) from tabPOL pol where pol.branch = vl.branch and pol.docstatus = 1 and pol.pol_type = e.hsd_type) as rate, e.hsd_type,
	(select em.tank_capacity from  `tabEquipment Model` em where em.name = e.equipment_model) as cap,
	CASE
	WHEN vl.ys_km THEN vl.ys_km
	else 0
	end as yskm,
	CASE
	WHEN vl.ys_hours THEN vl.ys_hours
	else 0
	end as yshour
	from `tabEquipment` e, `tabVehicle Logbook` vl where e.equipment_number = vl.equipment_number
	and vl.docstatus = 1"""  %{"from_date": str(filters.from_date), "to_date": str(filters.to_date),"branch": str(filters.branch)}