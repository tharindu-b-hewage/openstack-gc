### HTTP REST API endpoints for Green Cores controller

- `/gc-controller/sleep-info`
    - **GET**: Lists available CPU core sleep levels
- `/gc-controller/sleep`
    - **POST**: Put the given number of cores into sleep mode. This is a blocking operation, such that invoker can guarantee core sleep operations.