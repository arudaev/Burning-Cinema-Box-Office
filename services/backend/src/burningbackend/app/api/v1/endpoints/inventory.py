from typing import Optional

from fastapi import APIRouter, Depends, HTTPException

from burningbackend.app.core.deps import get_current_user
from burningbackend.app.models.inventory import Inventory, UpdateInventory
from burningbackend.app.models.user import User

router = APIRouter()


@router.post("/", response_description="Inventory added to the database")
async def add_inventory(inventory: Inventory, _: User = Depends(get_current_user)) -> dict:
    await inventory.create()
    inventory = await Inventory.find_one({"name": inventory.name})
    return {"message": "Inventory added successfully", "data": inventory}


@router.get("/", response_description="Inventory retrieved")
async def get_inventory(name: Optional[str] = None) -> list[Inventory]:
    if name:
        return await Inventory.find({"name": {"$regex": f".*{name}.*", "$options": "i"}}).to_list()
    return await Inventory.all().to_list()


@router.get("/{id}", response_description="Inventory retrieved")
async def get_inventory_by_id(id: str) -> Inventory:
    inventory = await Inventory.get(id)
    if inventory is None:
        raise HTTPException(status_code=404, detail="Inventory record not found")
    return inventory


@router.put("/sold/{id}", response_description="Inventory sold amount updated")
async def update_inventory_sold(id: str, amount: int, _: User = Depends(get_current_user)) -> dict:
    inventory = await Inventory.get(id)
    if not inventory:
        raise HTTPException(status_code=404, detail="Inventory record not found")
    if inventory.amount - amount < 0:
        raise HTTPException(status_code=422, detail="Insufficient stock")
    inventory.amount_sold += amount
    inventory.amount -= amount
    await inventory.save()
    return {"message": "Inventory updated successfully", "data": inventory}


@router.put("/{id}", response_description="Inventory data updated")
async def update_inventory(id: str, req: UpdateInventory, _: User = Depends(get_current_user)) -> dict:
    inventory = await Inventory.get(id)
    if not inventory:
        raise HTTPException(status_code=404, detail="Inventory record not found")
    update_data = {k: v for k, v in req.dict().items() if v is not None}
    updated_inventory = await inventory.update({"$set": update_data})
    return {"message": "Inventory updated successfully", "data": updated_inventory}


@router.delete("/{id}", response_description="Inventory deleted from the database")
async def delete_inventory(id: str, _: User = Depends(get_current_user)) -> dict:
    inventory = await Inventory.get(id)
    if not inventory:
        raise HTTPException(status_code=404, detail="Inventory record not found")
    await inventory.delete()
    return {"message": "Inventory deleted successfully"}
