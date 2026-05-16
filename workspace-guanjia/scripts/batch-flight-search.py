#!/usr/bin/env python3
"""Batch search all Shanghai-Seoul flight combinations (nonstop only)."""

import sys
import json
import time
import os
from datetime import datetime, timedelta

sys.path.insert(0, '/Users/georginalau/.openclaw/skills/available/flightclaw/scripts')
from search_utils import search_with_currency
from fli.models import Airport, FlightSearchFilters, FlightSegment, PassengerInfo, SeatType, TripType, MaxStops

# All four airport pairs
AIRPORT_PAIRS = [
    ('SHA', 'ICN'), ('SHA', 'GMP'),
    ('PVG', 'ICN'), ('PVG', 'GMP'),
]

# Valid combinations: (departure_dow, return_dow, nights)
# 周四出发+周六回 / 周四出发+周日回 / 周五出发+周六回 / 周五出发+周日回
THURSDAY = 3
FRIDAY = 4
SATURDAY = 5
SUNDAY = 6

USD_TO_CNY = 7.3

def get_valid_dates(year=2026):
    """Get all valid (depart, return) date pairs from 2026-04-09 to 2026-07-08."""
    start = datetime(year, 4, 23)  # First valid Thursday after today
    end = datetime(year, 7, 8)
    valid = []
    current = start
    while current <= end:
        if current.weekday() == THURSDAY:
            sat = current + timedelta(days=2)
            if sat <= end:
                valid.append((current.date(), sat.date(), 2))
            sun = current + timedelta(days=3)
            if sun <= end:
                valid.append((current.date(), sun.date(), 3))
        elif current.weekday() == FRIDAY:
            sat = current + timedelta(days=1)
            if sat <= end:
                valid.append((current.date(), sat.date(), 1))
            sun = current + timedelta(days=2)
            if sun <= end:
                valid.append((current.date(), sun.date(), 2))
        current += timedelta(days=1)
    return valid


def search_return(dep_ap, arr_ap, depart_date_str, return_date_str, retries=6, wait=30):
    """Search return flights (nonstop only)."""
    for attempt in range(retries):
        try:
            origin = Airport[dep_ap]
            destination = Airport[arr_ap]
            segments = [
                FlightSegment(departure_airport=[[origin, 0]], arrival_airport=[[destination, 0]], travel_date=depart_date_str),
                FlightSegment(departure_airport=[[destination, 0]], arrival_airport=[[origin, 0]], travel_date=return_date_str),
            ]
            filters = FlightSearchFilters(
                trip_type=TripType.ROUND_TRIP,
                passenger_info=PassengerInfo(adults=1),
                flight_segments=segments,
                seat_type=SeatType.ECONOMY,
                stops=MaxStops.NON_STOP,
            )
            results, currency = search_with_currency(filters, top_n=5)
            combos = []
            if results:
                for r in results:
                    flight_data = r[0]
                    if isinstance(flight_data[0], list):
                        ob_flights = flight_data[0]
                        ret_flights = flight_data[1]
                    else:
                        ob_flights = [flight_data[0]]
                        ret_flights = [flight_data[1]] if len(flight_data) > 1 else []

                    if not ob_flights or not ret_flights:
                        continue

                    ob = ob_flights[0]
                    rt = ret_flights[0]
                    combos.append({
                        'outbound': {
                            'price': ob.price,
                            'currency': currency,
                            'dep_time': ob.legs[0].departure_datetime.strftime('%H:%M'),
                            'arr_time': ob.legs[-1].arrival_datetime.strftime('%H:%M'),
                            'flight_no': "%s %s" % (ob.legs[0].airline.name, ob.legs[0].flight_number),
                            'total_price': ob.price + rt.price,
                        },
                        'return': {
                            'price': rt.price,
                            'currency': currency,
                            'dep_time': rt.legs[0].departure_datetime.strftime('%H:%M'),
                            'arr_time': rt.legs[-1].arrival_datetime.strftime('%H:%M'),
                            'flight_no': "%s %s" % (rt.legs[0].airline.name, rt.legs[0].flight_number),
                        },
                        'currency': currency,
                    })
            return combos
        except Exception as e:
            err_str = str(e)
            if '429' in err_str or 'rate' in err_str.lower():
                wait_time = wait * (attempt + 1)
                print("  429/rate hit, waiting %ds (attempt %d/%d)..." % (wait_time, attempt+1, retries), file=sys.stderr)
                time.sleep(wait_time)
            else:
                print("  Error: %s" % err_str, file=sys.stderr)
                break
    return []


def main():
    valid_dates = get_valid_dates()
    print("Total date combinations: %d" % len(valid_dates))
    print("Total airport pairs: %d" % len(AIRPORT_PAIRS))
    print("Total searches: %d" % (len(valid_dates) * len(AIRPORT_PAIRS)))

    outfile = '/Users/georginalau/.openclaw/workspace-guanjia/memory/flight-results.json'
    done_file = '/Users/georginalau/.openclaw/workspace-guanjia/memory/flight-done.json'

    done = set()
    if os.path.exists(done_file):
        done = set(json.load(open(done_file)))

    results = []
    if os.path.exists(outfile):
        results = json.load(open(outfile))

    total = len(valid_dates) * len(AIRPORT_PAIRS)
    idx = 0

    for ap_idx, (dep_ap, arr_ap) in enumerate(AIRPORT_PAIRS):
        for date_idx, (dep_date, ret_date, nights) in enumerate(valid_dates):
            key = "%d-%d" % (ap_idx, date_idx)
            if key in done:
                continue

            idx += 1
            dep_str = dep_date.strftime('%Y-%m-%d')
            ret_str = ret_date.strftime('%Y-%m-%d')
            print("[%d/%d] %s->%s | %s -> %s (%d nights)..." % (
                idx, total, dep_ap, arr_ap, dep_str, ret_str, nights))

            combos = search_return(dep_ap, arr_ap, dep_str, ret_str, retries=6, wait=30)

            if combos:
                filtered = []
                for c in combos:
                    ob_dep_h = int(c['outbound']['dep_time'].split(':')[0])
                    rt_arr_h = int(c['return']['arr_time'].split(':')[0])
                    rt_arr_m = int(c['return']['arr_time'].split(':')[1])

                    # Departure after 08:00
                    if ob_dep_h < 8:
                        continue
                    # Return arrival before 21:00
                    if rt_arr_h > 21 or (rt_arr_h == 21 and rt_arr_m > 0):
                        continue

                    filtered.append({
                        'dep_airport': dep_ap,
                        'arr_airport': arr_ap,
                        'depart_date': dep_str,
                        'return_date': ret_str,
                        'nights': nights,
                        'outbound': c['outbound'],
                        'return': c['return'],
                        'total_price': c['outbound']['total_price'],
                        'currency': c['currency'],
                    })

                if filtered:
                    best = min(filtered, key=lambda x: x['total_price'])
                    results.append(best)
                    total_cny = int(best['total_price'] * USD_TO_CNY)
                    print("  BEST: %s %s-%s ($%d) + %s %s-%s ($%d) = $%d (~%dCNY)" % (
                        best['outbound']['flight_no'], best['outbound']['dep_time'], best['outbound']['arr_time'],
                        int(best['outbound']['price']),
                        best['return']['flight_no'], best['return']['dep_time'], best['return']['arr_time'],
                        int(best['return']['price']),
                        int(best['total_price']), total_cny))
                else:
                    print("  No combos meeting time constraints")
            else:
                print("  No results (rate limited or no flights)")

            # Save progress
            with open(outfile, 'w') as f:
                json.dump(results, f, indent=2, ensure_ascii=False)
            done.add(key)
            with open(done_file, 'w') as f:
                json.dump(list(done), f)

            # Delay between calls
            print("  Waiting 25s...")
            time.sleep(25)

    print("")
    print("=" * 60)
    print("DONE! %d valid combinations found." % len(results))
    print("=" * 60)

    results.sort(key=lambda x: x['total_price'])
    print("\nTOP 30 CHEAPEST (Nonstop, Dep>=08:00, Ret<=21:00):\n")
    for i, r in enumerate(results[:30]):
        total_cny = int(r['total_price'] * USD_TO_CNY)
        print("%d. %s->%s | %s(%d nights) | Out:%s %s-%s | Ret:%s %s-%s | ~%dCNY" % (
            i+1, r['dep_airport'], r['arr_airport'], r['depart_date'], r['nights'],
            r['outbound']['flight_no'], r['outbound']['dep_time'], r['outbound']['arr_time'],
            r['return']['flight_no'], r['return']['dep_time'], r['return']['arr_time'],
            total_cny))

    # Also show under 1500 CNY threshold
    print("\nUNDER 1500 CNY:")
    under1500 = [r for r in results if int(r['total_price'] * USD_TO_CNY) <= 1500]
    if under1500:
        for i, r in enumerate(under1500):
            total_cny = int(r['total_price'] * USD_TO_CNY)
            print("  %s->%s | %s(%d nights) | Out:%s %s | Ret:%s %s | ~%dCNY" % (
                r['dep_airport'], r['arr_airport'], r['depart_date'], r['nights'],
                r['outbound']['flight_no'], r['outbound']['dep_time'],
                r['return']['flight_no'], r['return']['arr_time'],
                total_cny))
    else:
        print("  None found.")

    print("\nUNDER 1200 CNY (甩尾票):")
    under1200 = [r for r in results if int(r['total_price'] * USD_TO_CNY) <= 1200]
    if under1200:
        for i, r in enumerate(under1200):
            total_cny = int(r['total_price'] * USD_TO_CNY)
            print("  %s->%s | %s(%d nights) | Out:%s %s | Ret:%s %s | ~%dCNY" % (
                r['dep_airport'], r['arr_airport'], r['depart_date'], r['nights'],
                r['outbound']['flight_no'], r['outbound']['dep_time'],
                r['return']['flight_no'], r['return']['arr_time'],
                total_cny))
    else:
        print("  None found.")


if __name__ == '__main__':
    main()
