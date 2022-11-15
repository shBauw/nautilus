coverage run nautilus.py < e2e_tests/test1.in | diff e2e_tests/test1.out -
coverage run -a nautilus.py < e2e_tests/test2.in | diff e2e_tests/test2.out -
coverage run -a nautilus.py < e2e_tests/test3.in | diff e2e_tests/test3.out -
coverage run -a nautilus.py < e2e_tests/test4.in | diff e2e_tests/test4.out -
coverage run -a nautilus.py < e2e_tests/test5.in | diff e2e_tests/test5.out -
coverage run -a nautilus.py < e2e_tests/test6.in | diff e2e_tests/test6.out -
coverage run -a nautilus.py < e2e_tests/test7.in | diff e2e_tests/test7.out -
coverage run -a nautilus.py < e2e_tests/test8.in | diff e2e_tests/test8.out -
coverage run -a nautilus.py < e2e_tests/test9.in | diff e2e_tests/test9.out -
coverage run -a nautilus.py < e2e_tests/test10.in | diff e2e_tests/test10.out -
coverage run -a nautilus.py < e2e_tests/test11.in | diff e2e_tests/test11.out -

coverage report
coverage html