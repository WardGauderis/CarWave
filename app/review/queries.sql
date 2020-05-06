-- get tags for user
select tag.title
from tag
         join review r on tag.review_id = r.id
where r.to_id = 2
  and r.as_driver = false
group by tag.title
order by count(tag.title) desc
limit 10;

-- get avg user rating
select avg(review.rating)
from review
where review.to_id = 2;

-- get drives in which user took place in the past
select ride_id
from rides
         join passenger_requests pr on rides.id = pr.ride_id and pr.status = 'accepted'
where rides.arrival_time < now()
    and rides.driver_id = 1
   or pr.user_id = 1;

-- insert or update review
insert into review(from_id, to_id, as_driver, review, rating, last_modified)
values (2, 1, false, 'mss hallo', 5, now())
on conflict on constraint one_review do update set review=excluded.review,
                                                   rating=excluded.rating,
                                                   last_modified=excluded.last_modified;

-- driver review
select case
           when exists(
                   select ride_id
                   from rides
                            join passenger_requests pr on rides.id = pr.ride_id and pr.status = 'accepted'
                   where rides.arrival_time < now() and 1!=2
                     and (pr.user_id = 1 and rides.driver_id = 2)
               ) then 1
           else 0
           end;

--  passenger review
select case
           when exists(
                   select r.id
                   from rides r
                            join passenger_requests pr1 on r.id = pr1.ride_id and pr1.status = 'accepted'
                            join passenger_requests pr2 on r.id = pr2.ride_id and pr2.status = 'accepted'
                   where r.arrival_time < now() and 1 != 2
                       and pr1.user_id = 1 and pr2.user_id = 2
                      or r.driver_id = 1 and pr1.user_id = 2) then 1
           else 0 end;

-- autocompletion
select title from tag where lower(title) like '%c%' group by tag.title order by count(tag.title) desc