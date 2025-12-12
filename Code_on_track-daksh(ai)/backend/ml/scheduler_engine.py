from ortools.constraint_solver import routing_enums_pb2
from ortools.constraint_solver import pywrapcp
from sqlalchemy import text
from services.db import db
import pandas as pd
import json
from datetime import datetime

def create_data_model(lots, num_vehicles=2):
    """Stores the data for the problem."""
    data = {}
    
    # Service times in minutes based on risk
    # Critical: 40, High: 30, Medium: 20, Low: 15
    service_times = []
    ids = []
    risks = []
    task_descs = []
    lot_nos = []
    
    # Node 0 is the depot (start/end)
    service_times.append(0)
    ids.append("DEPOT")
    risks.append("N/A")
    task_descs.append("Start/End")
    lot_nos.append("DEPOT")

    for lot in lots:
        risk = lot.get('risk_level', 'LOW')
        if risk == 'CRITICAL':
            time = 40
        elif risk == 'HIGH':
            time = 30
        elif risk == 'MEDIUM':
            time = 20
        else:
            time = 15
            
        service_times.append(time)
        ids.append(lot.get('lot_no'))
        risks.append(risk)
        task_descs.append(lot.get('recommended_action', 'Monitor'))
        lot_nos.append(lot.get('lot_no'))

    data['service_times'] = service_times
    data['ids'] = ids
    data['risks'] = risks
    data['tasks'] = task_descs
    data['lot_nos'] = lot_nos
    
    # Distance matrix: cost to travel between nodes.
    # We assume travel time is negligible within a depot for this simplified model,
    # OR we can add a constant travel time (e.g., 10 mins) between jobs.
    # The constraint is mostly service time.
    # Let's add a small travel buffer of 10 mins between sites.
    travel_time = 10
    size = len(service_times)
    matrix = {}
    for from_node in range(size):
        matrix[from_node] = {}
        for to_node in range(size):
            if from_node == to_node:
                matrix[from_node][to_node] = 0
            else:
                # Cost = travel time + service time of the destination?
                # VRP standard: Arc cost is travel. Service time is a dimension.
                # But typically we want to limit Total Time = Travel + Service.
                # We will model Time Dimension correctly.
                matrix[from_node][to_node] = travel_time

    data['distance_matrix'] = matrix
    data['num_vehicles'] = num_vehicles
    data['depot'] = 0
    return data

def generate_optimal_routes(limit_hours=8):
    """
    optimize routes using OR-Tools
    """
    print("Starting Scheduler Optimization...")
    
    # 1. Fetch lots
    # We join lot_health to get risk scores.
    sql = text("""
        SELECT 
            lh.lot_no, lh.risk_level, lh.health_score, lh.recommended_action,
            COALESCE(i.depot, 'General') as depot
        FROM lot_health lh
        LEFT JOIN (
            SELECT DISTINCT lot_no, depot FROM items
        ) i ON lh.lot_no = i.lot_no
        where lh.risk_level IN ('CRITICAL', 'HIGH', 'MEDIUM') -- Prioritize these
        ORDER BY lh.health_score ASC
        LIMIT 50 -- Limit for demo performance
    """)
    
    try:
        conn = db.session.connection()
        df = pd.read_sql(sql, conn)
    except Exception as e:
        print(f"Error fetching data: {e}")
        return {"error": str(e)}
        
    if df.empty:
        return {"routes": [], "message": "No high risk lots to schedule."}

    # Group by depot
    depots = df['depot'].unique()
    all_routes = []
    
    for depot_name in depots:
        depot_lots = df[df['depot'] == depot_name].to_dict('records')
        
        # Instantiate the data problem.
        # Number of teams per depot: Dynamic or fixed? Let's say 2 teams per depot.
        data = create_data_model(depot_lots, num_vehicles=2)
        
        # Create Routing Index Manager
        manager = pywrapcp.RoutingIndexManager(len(data['distance_matrix']),
                                               data['num_vehicles'], data['depot'])

        # Create Routing Model
        routing = pywrapcp.RoutingModel(manager)

        # Create and register a transit callback.
        def distance_callback(from_index, to_index):
            from_node = manager.IndexToNode(from_index)
            to_node = manager.IndexToNode(to_index)
            return data['distance_matrix'][from_node][to_node]

        transit_callback_index = routing.RegisterTransitCallback(distance_callback)
        routing.SetArcCostEvaluatorOfAllVehicles(transit_callback_index)

        # Add Time Dimension (Travel + Service Time)
        def time_callback(from_index, to_index):
            from_node = manager.IndexToNode(from_index)
            to_node = manager.IndexToNode(to_index)
            # Travel time + Service time at destination
            return data['distance_matrix'][from_node][to_node] + data['service_times'][to_node]

        time_callback_index = routing.RegisterTransitCallback(time_callback)
        
        # Max limit 8 hours = 480 minutes
        # Allow waiting time? No.
        routing.AddDimension(
            time_callback_index,
            30,  # slack (waiting time allowed)
            limit_hours * 60,  # vehicle maximum capacity (minutes)
            True,  # start cumul to zero
            "Time"
        )
        
        # Add Penalty for dropping nodes (so solver doesn't fail if tight)
        # Critical lots should have huge penalty to drop.
        penalty = 100000
        for node in range(1, len(data['distance_matrix'])):
            routing.AddDisjunction([manager.NodeToIndex(node)], penalty)

        # Setting first solution heuristic.
        search_parameters = pywrapcp.DefaultRoutingSearchParameters()
        search_parameters.first_solution_strategy = (
            routing_enums_pb2.FirstSolutionStrategy.PATH_CHEAPEST_ARC)

        # Solve the problem.
        solution = routing.SolveWithParameters(search_parameters)

        # Print solution on console.
        if solution:
            time_dimension = routing.GetDimensionOrDie("Time")
            for vehicle_id in range(data['num_vehicles']):
                index = routing.Start(vehicle_id)
                route_lots = []
                route_load = 0
                
                while not routing.IsEnd(index):
                    node_index = manager.IndexToNode(index)
                    time_var = time_dimension.CumulVar(index)
                    
                    if node_index != 0: # Skip depot in list
                        route_lots.append({
                            "lot_no": data['lot_nos'][node_index],
                            "risk": data['risks'][node_index],
                            "task": data['tasks'][node_index],
                            "eta": f"start + {solution.Min(time_var)}m"
                        })
                    
                    index = solution.Value(routing.NextVar(index))
                    route_load = solution.Min(time_dimension.CumulVar(index))
                
                # Only add non-empty routes
                if route_lots:
                    all_routes.append({
                        "team": f"{depot_name}-Team-{vehicle_id + 1}",
                        "depot": depot_name,
                        "lots": route_lots,
                        "total_hours": round(route_load / 60, 2)
                    })
                    
    summary_lines = []
    total_lots = 0
    for r in all_routes:
        count = len(r['lots'])
        total_lots += count
        summary_lines.append(f"{r['team']}: {count} lots ({r['total_hours']}h)")
    
    summary_text = f"Optimized schedule covers {total_lots} critical lots across {len(all_routes)} teams.\n" + "\n".join(summary_lines)

    return {"routes": all_routes, "summary": summary_text}
